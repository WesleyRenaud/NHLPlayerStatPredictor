from ..player_names.player_names_routes import PlayerNamesRoutes
from .post_route_registry import PostRouteRegistry
from ..projections.projections_routes import ProjectionsRoutes


PostRouteRegistry.register( PlayerNamesRoutes.ROUTES )
PostRouteRegistry.register( ProjectionsRoutes.ROUTES )
