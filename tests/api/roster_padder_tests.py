from __future__ import annotations

from api.depth_group import DepthGroup
from api.league_filler import LeagueFiller
from api.projections.current_season_nhl_skater import CurrentSeasonNhlSkater
from api.projections.nhl_lineup_selector import NhlLineupSelector
from api.projections.season_pace import SeasonPace
from api.roster_padder import RosterPadder
from api.shared.enums.position import Position
from api.skater_position import SkaterPosition
from api.slot_average import SlotAverage
from api.team import Team


def _defense( player_id: int, team: Team ) -> CurrentSeasonNhlSkater:
   return CurrentSeasonNhlSkater(
      player_id,
      SeasonPace( 4.0, 8.0 ),
      team,
      SkaterPosition( 'D' ) )


def _forward( player_id: int, team: Team ) -> CurrentSeasonNhlSkater:
   return CurrentSeasonNhlSkater(
      player_id,
      SeasonPace( 10.0, 12.0 ),
      team,
      SkaterPosition( 'C' ) )


def Test_Pad_TestSixDefense_ExpectSeventhPace() -> None:
   team = list( Team )[ Position.FIRST ]
   slots = [ SlotAverage( 7, 15.0, 2.5, 12.5 ) ]
   padded = RosterPadder.pad(
      [ _defense( index, team ) for index in range( 1, NhlLineupSelector.DEFENSE ) ],
      slots )
   seventh = next(
      skater
      for skater in padded
      if LeagueFiller.is_filler( skater.player_id ) )
   assert seventh.contribution == slots[ Position.FIRST ].contribution
   assert seventh.position == SkaterPosition( 'D' )
   assert len(
      [
         skater
         for skater in padded
         if DepthGroup.defense().contains( skater.position )
      ] ) == NhlLineupSelector.DEFENSE


def Test_Pad_TestFullDefense_ExpectUnchanged() -> None:
   team = list( Team )[ Position.FIRST ]
   rows = [
      _defense( index, team )
      for index in range( 1, NhlLineupSelector.DEFENSE + 1 )
   ]
   assert RosterPadder.pad(
      rows,
      [ SlotAverage( 7, 15.0, 2.5, 12.5 ) ] ) == rows


def Test_Pad_TestTwelveForwards_ExpectThirteenthPace() -> None:
   team = list( Team )[ Position.FIRST ]
   group = DepthGroup.forwards()
   slots = [ SlotAverage( group.spare_slot, 11.0, 8.0, 10.0 ) ]
   padded = RosterPadder.pad(
      [ _forward( index, team ) for index in range( 1, group.roster_count ) ],
      slots )
   thirteenth = next(
      skater
      for skater in padded
      if LeagueFiller.is_filler( skater.player_id ) )
   assert thirteenth.contribution == slots[ Position.FIRST ].contribution
   assert thirteenth.position == SkaterPosition( 'F' )
   assert len(
      [
         skater
         for skater in padded
         if group.contains( skater.position )
      ] ) == group.roster_count
