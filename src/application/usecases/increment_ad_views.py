from src.application.exceptions import AdNotFoundError
from src.application.ports.uow import UnitOfWork
from src.application.ports.usecases import IncrementAdViewsPort
from src.domain.entities import Ad, AdStatus


class IncrementAdViews(IncrementAdViewsPort):
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, ad_id: int) -> Ad:
        async with self._uow:
            ad = await self._uow.ads.get_by_id(ad_id)
            if ad is None or ad.status == AdStatus.ARCHIVED:
                raise AdNotFoundError
            ad.register_view()
            await self._uow.ads.increment_views(ad_id)
            await self._uow.commit()
        return ad
