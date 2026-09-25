from __future__ import annotations

from api.availability.games_share import GamesShare
from api.depth.depth_group import DepthGroup
from api.team_factor.teammate_mixer import TeammateMixer
from api.team_factor.teammate_skater import TeammateSkater


def _regular(
      player_id: int,
      contribution: float,
      availability: float,
      prior_availability: float | None ) -> TeammateSkater:
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
   regulars = [
      _regular( index, 20.0, GamesShare.FULL, None )
      for index in range( 1, 7 )
   ]
   extras = [ _regular( 7, 10.0, GamesShare.FULL, None ) ]
   assert _expected( regulars, extras ) == 120.0


def Test_Expected_TestOneAlwaysOut_ExpectExtraFills() -> None:
   regulars = [
      *[
         _regular( index, 20.0, GamesShare.FULL, None )
         for index in range( 1, 6 )
      ],
      _regular( 6, 20.0, 0.0, None ),
   ]
   extras = [ _regular( 7, 10.0, GamesShare.FULL, None ) ]
   assert _expected( regulars, extras ) == 110.0


def Test_Expected_TestHalfOut_ExpectMix() -> None:
   regulars = [
      *[
         _regular( index, 20.0, GamesShare.FULL, None )
         for index in range( 1, 6 )
      ],
      _regular( 6, 20.0, 0.5, None ),
   ]
   extras = [ _regular( 7, 10.0, GamesShare.FULL, None ) ]
   assert abs( _expected( regulars, extras ) - 115.0 ) < 0.001


def Test_Teammates_TestHealthyRegular_ExpectOtherFive() -> None:
   regulars = [
      _regular( index, 20.0, GamesShare.FULL, None )
      for index in range( 1, 7 )
   ]
   assert _teammates(
      1,
      regulars,
      [ _regular( 7, 10.0, GamesShare.FULL, None ) ] ) == 100.0


def Test_Teammates_TestInjuredRegular_ExpectHealthyFive() -> None:
   regulars = [
      _regular( 1, 20.0, 0.5, None ),
      *[
         _regular( index, 20.0, GamesShare.FULL, None )
         for index in range( 2, 7 )
      ],
   ]
   extras = [ _regular( 7, 10.0, GamesShare.FULL, None ) ]
   assert _teammates( 1, regulars, extras ) == 100.0
   assert abs( _teammates( 2, regulars, extras ) - 95.0 ) < 0.001


def Test_Expected_TestPriorSet_ExpectCurrentMix() -> None:
   regulars = [
      *[
         _regular( index, 20.0, GamesShare.FULL, 0.5 )
         for index in range( 1, 6 )
      ],
      _regular( 6, 20.0, 0.5, 0.0 ),
   ]
   extras = [ _regular( 7, 10.0, GamesShare.FULL, None ) ]
   assert abs( _expected( regulars, extras ) - 115.0 ) < 0.001


def Test_Expected_TestPriorSicker_ExpectCurrentHealthy() -> None:
   regulars = [
      *[
         _regular( index, 20.0, GamesShare.FULL, GamesShare.FULL )
         for index in range( 1, 6 )
      ],
      _regular( 6, 20.0, GamesShare.FULL, 0.0 ),
   ]
   extras = [ _regular( 7, 10.0, GamesShare.FULL, None ) ]
   assert _expected( regulars, extras ) == 120.0
