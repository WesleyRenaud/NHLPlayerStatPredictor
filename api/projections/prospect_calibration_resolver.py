from __future__ import annotations

from dataclasses import replace

from ..aging.league_factor import LeagueFactor
from .draft_pick_modifier_fitter import DraftPickModifierFitter
from .pace_values import PaceValues
from .prospect_calibration_model import ProspectCalibrationModel
from .prospect_calibration_store import ProspectCalibrationStore
from .prospect_eligibility import ProspectEligibility
from .prospect_profile import ProspectProfile
from .prospect_source_resolver import ProspectSourceResolver
from ..season import Season
from ..skaters.other_league_skater_season import OtherLeagueSkaterSeason
from ..skaters.skater import Skater


class ProspectCalibrationResolver():
   MAX_DRAFT_PICK = 32


   @classmethod
   def adjust(
         cls,
         skater: Skater,
         target_season_id: int,
         paces: PaceValues,
         league_factors: list[ LeagueFactor ] ) -> PaceValues:
      source = ProspectSourceResolver.latest(
         skater.seasons, target_season_id,
         supported_leagues={ factor.league for factor in league_factors } )
      if source is None:
         return paces
      model = ProspectCalibrationStore.read()
      profile = cls._profile_for( model, source.player_id )
      pick = cls._eligible_pick( profile, source, target_season_id )
      if pick is None:
         return paces
      modifier = DraftPickModifierFitter.fit( model.samples, target_season_id, excluded_player_id=source.player_id )
      return cls._scale_scoring( paces, modifier.factor( pick ) )


   @classmethod
   def _profile_for(
         cls,
         model: ProspectCalibrationModel,
         player_id: int ) -> ProspectProfile:
      return next( profile for profile in model.profiles if profile.player_id == player_id )


   @classmethod
   def _eligible_pick(
         cls,
         profile: ProspectProfile,
         source: OtherLeagueSkaterSeason,
         target_season_id: int ) -> int | None:
      pick = profile.draft_pick_before( target_season_id ).value
      if pick is None or pick > cls.MAX_DRAFT_PICK:
         return None
      age = source.completed_age() + Season.start_year( target_season_id ) - Season.start_year( source.season_id )
      if not ProspectEligibility.eligible( profile, target_season_id, age ):
         return None
      return pick


   @classmethod
   def _scale_scoring( cls, paces: PaceValues, factor: float ) -> PaceValues:
      return replace(
         paces,
         even_strength_goals=paces.even_strength_goals * factor,
         even_strength_assists=paces.even_strength_assists * factor,
         power_play_goals=paces.power_play_goals * factor,
         power_play_assists=paces.power_play_assists * factor,
         short_handed_goals=paces.short_handed_goals * factor,
         short_handed_assists=paces.short_handed_assists * factor )
