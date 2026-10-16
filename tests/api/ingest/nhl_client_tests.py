from api.ingest.nhl_client import NhlClient


def Test_GamePageParams_TestGameLines_ExpectGameBreakdown() -> None:
   cayenne = 'seasonId=20242025'

   params = NhlClient._game_page_params( cayenne )

   assert params[ 'isGame' ] == 'true'
   assert params[ 'sort' ] == 'gameDate'
   assert params[ 'cayenneExp' ] == cayenne


def Test_PageParams_TestSeasonTotals_ExpectPlayerSort() -> None:
   params = NhlClient._page_params( 'seasonId=20242025' )

   assert params[ 'isGame' ] == 'false'
   assert params[ 'sort' ] == 'playerId'
