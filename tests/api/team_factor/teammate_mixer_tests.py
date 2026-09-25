from __future__ import annotations

from api.availability.games_share import GamesShare
from api.depth.depth_group import DepthGroup
from api.shared.enums.position import Position
from api.team_factor.teammate_mixer import TeammateMixer
from api.team_factor.teammate_skater import TeammateSkater


def _regular(
      player_id: int,
      contribution: float,
      availability: float,
      prior_availability: float | None = None ) -> TeammateSkater:
   return TeammateSkater(
      player_id,
      contribution,
      availability,
      prior_availability )


def _expected(
      regulars: list[ TeammateSkater ],
      extras: list[ TeammateSkater ] ) -> float:
   return TeammateMixer.expected(
      regulars,
      extras,
      [],
      DepthGroup.defense() )


def _teammates(
      player_id: int,
      regulars: list[ TeammateSkater ],
      extras: list[ TeammateSkater ] ) -> float:
   return TeammateMixer.teammates(
      player_id,
      regulars,
      extras,
      [],
      DepthGroup.defense() )


def Test_Expected_TestHealthySix_ExpectRegularsOnly() -> None:
   group = DepthGroup.defense()
   pace = 20.0
   extra_pace = 10.0
   regulars = [
      _regular( index, pace, GamesShare.FULL )
      for index in range( 1, group.dressed_count + 1 )
   ]
   extras = [ _regular( group.dressed_count + 1, extra_pace, GamesShare.FULL ) ]

   total = _expected( regulars, extras )

   assert total == sum( skater.contribution for skater in regulars )


def Test_Expected_TestOneAlwaysOut_ExpectExtraFills() -> None:
   group = DepthGroup.defense()
   pace = 20.0
   extra_pace = 10.0
   out = _regular( group.dressed_count, pace, 0.0 )
   regulars = [
      *[
         _regular( index, pace, GamesShare.FULL )
         for index in range( 1, group.dressed_count )
      ],
      out,
   ]
   extras = [ _regular( group.dressed_count + 1, extra_pace, GamesShare.FULL ) ]

   total = _expected( regulars, extras )

   playing = [ skater for skater in regulars if skater.availability ]
   assert total == (
      sum( skater.contribution for skater in playing )
      + extras[ Position.FIRST ].contribution )


def Test_Expected_TestHalfOut_ExpectMix() -> None:
   group = DepthGroup.defense()
   pace = 20.0
   extra_pace = 10.0
   injured = _regular( group.dressed_count, pace, 0.5 )
   regulars = [
      *[
         _regular( index, pace, GamesShare.FULL )
         for index in range( 1, group.dressed_count )
      ],
      injured,
   ]
   extras = [ _regular( group.dressed_count + 1, extra_pace, GamesShare.FULL ) ]

   total = _expected( regulars, extras )

   healthy = sum( skater.contribution for skater in regulars )
   filled = (
      sum( skater.contribution for skater in regulars if skater is not injured )
      + extras[ Position.FIRST ].contribution )
   assert abs(
      total
      - injured.availability * healthy
      - ( 1.0 - injured.availability ) * filled ) < 0.001


def Test_Teammates_TestHealthyRegular_ExpectOtherFive() -> None:
   group = DepthGroup.defense()
   pace = 20.0
   extra_pace = 10.0
   regulars = [
      _regular( index, pace, GamesShare.FULL )
      for index in range( 1, group.dressed_count + 1 )
   ]
   extras = [ _regular( group.dressed_count + 1, extra_pace, GamesShare.FULL ) ]
   player = regulars[ Position.FIRST ]

   teammates = _teammates( player.player_id, regulars, extras )

   others = [
      skater
      for skater in regulars
      if skater.player_id != player.player_id
   ]
   assert teammates == sum( skater.contribution for skater in others )


def Test_Teammates_TestInjuredRegular_ExpectHealthyFive() -> None:
   group = DepthGroup.defense()
   pace = 20.0
   extra_pace = 10.0
   injured = _regular( 1, pace, 0.5 )
   healthy = _regular( 2, pace, GamesShare.FULL )
   rest = [
      _regular( index, pace, GamesShare.FULL )
      for index in range( 3, group.dressed_count + 1 )
   ]
   regulars = [ injured, healthy, *rest ]
   extras = [ _regular( group.dressed_count + 1, extra_pace, GamesShare.FULL ) ]

   when_injured_plays = _teammates( injured.player_id, regulars, extras )
   when_healthy_plays = _teammates( healthy.player_id, regulars, extras )

   others = [
      skater
      for skater in regulars
      if skater.player_id != injured.player_id
   ]
   assert when_injured_plays == sum( skater.contribution for skater in others )
   mixed = (
      injured.availability * injured.contribution
      + ( 1.0 - injured.availability ) * extras[ Position.FIRST ].contribution
      + sum( skater.contribution for skater in rest ) )
   assert abs( when_healthy_plays - mixed ) < 0.001


def Test_Expected_TestPriorSet_ExpectCurrentMix() -> None:
   group = DepthGroup.defense()
   pace = 20.0
   extra_pace = 10.0
   injured = _regular( group.dressed_count, pace, 0.5, 0.0 )
   regulars = [
      *[
         _regular( index, pace, GamesShare.FULL, 0.5 )
         for index in range( 1, group.dressed_count )
      ],
      injured,
   ]
   extras = [ _regular( group.dressed_count + 1, extra_pace, GamesShare.FULL ) ]

   total = _expected( regulars, extras )

   healthy = sum( skater.contribution for skater in regulars )
   filled = (
      sum( skater.contribution for skater in regulars if skater is not injured )
      + extras[ Position.FIRST ].contribution )
   assert abs(
      total
      - injured.availability * healthy
      - ( 1.0 - injured.availability ) * filled ) < 0.001


def Test_Expected_TestPriorSicker_ExpectCurrentHealthy() -> None:
   group = DepthGroup.defense()
   pace = 20.0
   extra_pace = 10.0
   regulars = [
      *[
         _regular( index, pace, GamesShare.FULL, GamesShare.FULL )
         for index in range( 1, group.dressed_count )
      ],
      _regular( group.dressed_count, pace, GamesShare.FULL, 0.0 ),
   ]
   extras = [ _regular( group.dressed_count + 1, extra_pace, GamesShare.FULL ) ]

   total = _expected( regulars, extras )

   assert total == sum( skater.contribution for skater in regulars )
