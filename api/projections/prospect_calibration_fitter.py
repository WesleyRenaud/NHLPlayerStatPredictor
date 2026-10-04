from __future__ import annotations

from itertools import groupby

from ..aging.aging_curve_fitter import AgingCurveFitter
from ..aging.league_factor_fitter import LeagueFactorFitter
from .baseline_pace_resolver import BaselinePaceResolver
from .prospect_calibration_candidate import ProspectCalibrationCandidate
from .prospect_calibration_model import ProspectCalibrationModel
from .prospect_calibration_sample import ProspectCalibrationSample
from .prospect_eligibility import ProspectEligibility
from .prospect_profile import ProspectProfile
from ..recency.pace_regression_fitter import PaceRegressionFitter
from ..recency.prior_year import PriorYear
from ..season import Season
from ..skaters.club_league import ClubLeague
from ..skaters.nhl_skater_season import NhlSkaterSeason
from ..skaters.other_league_skater_season import OtherLeagueSkaterSeason
from ..skaters.skater_history import SkaterHistory


class ProspectCalibrationFitter():
   MAX_SOURCE_GAP = 5


   @classmethod
   def fit(
         cls,
         histories: list[ SkaterHistory ],
         target_season_id: int,
         pace_games: int ) -> ProspectCalibrationModel:
      profiles: list[ ProspectProfile ] = []
      candidates: list[ ProspectCalibrationCandidate ] = []
      nhl_seasons: list[ NhlSkaterSeason ] = []
      other_seasons: list[ OtherLeagueSkaterSeason ] = []
      for history in histories:
         profile = history.profile
         profiles.append( profile )
         player_nhl_seasons = history.nhl_seasons()
         nhl_seasons.extend( player_nhl_seasons )
         other_seasons.extend( history.other_league_seasons() )
         for actual in sorted( player_nhl_seasons, key=lambda row: row.season_id ):
            if actual.games_played < PriorYear.MIN_GAMES or actual.season_id >= target_season_id:
               continue
            if not ProspectEligibility.eligible(
                  profile, actual.season_id, actual.completed_age() ):
               continue
            if history.latest_prospect_source(
                  actual.season_id, max_gap=cls.MAX_SOURCE_GAP,
                  supported_leagues={ league.value for league in ClubLeague } ) is not None:
               candidates.append( ProspectCalibrationCandidate( history, actual ) )
               break
      samples: list[ ProspectCalibrationSample ] = []
      for season_id, season_candidates in groupby(
            sorted( candidates, key=lambda candidate: candidate.outcome.season_id ),
            key=lambda candidate: candidate.outcome.season_id ):
         prior_nhl = [ row for row in nhl_seasons if row.season_id < season_id ]
         prior_other = [ row for row in other_seasons if row.season_id < season_id ]
         if not prior_nhl:
            continue
         factors = LeagueFactorFitter.fit(
            prior_nhl, prior_other, AgingCurveFitter.fit( prior_nhl, prior_other ) )
         baseline_model = PaceRegressionFitter.fit( prior_nhl, prior_other, factors )
         for candidate in season_candidates:
            history = candidate.history
            actual = candidate.outcome
            profile = history.profile
            source = history.latest_prospect_source(
               season_id, max_gap=cls.MAX_SOURCE_GAP,
               supported_leagues={ factor.league for factor in factors } )
            if source is None:
               continue
            paces = BaselinePaceResolver.resolve(
               history.before( season_id ),
               season_id, factors, baseline_model )
            if paces is None:
               continue
            samples.append( ProspectCalibrationSample(
               actual.player_id, season_id, profile.draft_pick_before( season_id ),
               paces.goals + paces.assists,
               Season.pace( actual.points, actual.games_played, pace_games ), source.league ) )
      return ProspectCalibrationModel( target_season_id, profiles, samples )
