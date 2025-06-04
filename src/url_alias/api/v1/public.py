from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from url_alias.domains.aliases.dependencies import get_alias_service
from url_alias.domains.aliases.services import AliasService
from url_alias.domains.statistics.dependencies import get_statistic_service
from url_alias.domains.statistics.services import StatisticService
from url_alias.shared.logging import get_logger
from url_alias.shared.rate_limiting import limiter

router = APIRouter()
logger = get_logger(__name__)


@router.get("/{short_code}")
@limiter.limit("30/minute")
async def redirect_to_url(
    request: Request,
    short_code: str,
    alias_service: AliasService = Depends(get_alias_service),
    statistic_service: StatisticService = Depends(get_statistic_service),
):
    """
    Redirect to the original URL using the short code. Public endpoint.
    Rate limited to 30 requests per minute per IP.
    """
    logger.info(f"Redirect request for short code: {short_code}")

    try:
        alias = await alias_service.get_active_alias_by_short_code(short_code)
        if not alias:
            logger.warning(f"Short code {short_code} not found or expired")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found or expired")

        try:
            await statistic_service.record_click(alias.id)
            logger.debug(f"Recorded click for alias {alias.id}")
        except Exception as e:
            logger.error(f"Failed to record click for alias {alias.id}: {str(e)}")

        logger.info(f"Redirecting {short_code} to: {alias.target_url}")

        response = RedirectResponse(url=alias.target_url, status_code=status.HTTP_302_FOUND)
        # Prevent the browser from caching the redirect
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing redirect for {short_code}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the redirect.",
        )
