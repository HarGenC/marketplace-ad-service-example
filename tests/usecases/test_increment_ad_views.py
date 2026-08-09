import pytest

from src.application.exceptions import AdNotFoundError
from src.application.usecases.create_ad import CreateAd
from src.application.usecases.delete_ad import DeleteAd
from src.application.usecases.increment_ad_views import IncrementAdViews
from src.domain.entities import Ad
from tests.conftest import FakeUnitOfWork


async def _create_ad(fake_uow: FakeUnitOfWork, user_id: int = 1) -> Ad:
    create = CreateAd(fake_uow)
    return await create.execute(
        user_id=user_id,
        title="T",
        description="d",
        price=100,
        category="c",
        city="x",
    )


@pytest.mark.asyncio
async def test_increment_views_bumps_counter(fake_uow: FakeUnitOfWork) -> None:
    created = await _create_ad(fake_uow)

    increment = IncrementAdViews(fake_uow)
    ad = await increment.execute(created.id)

    assert ad.views == 1

    stored = await fake_uow.ads.get_by_id(created.id)
    assert stored is not None
    assert stored.views == 1


@pytest.mark.asyncio
async def test_increment_views_accumulates(fake_uow: FakeUnitOfWork) -> None:
    created = await _create_ad(fake_uow)

    increment = IncrementAdViews(fake_uow)
    for _ in range(3):
        await increment.execute(created.id)

    stored = await fake_uow.ads.get_by_id(created.id)
    assert stored is not None
    assert stored.views == 3


@pytest.mark.asyncio
async def test_increment_views_does_not_touch_updated_at(
    fake_uow: FakeUnitOfWork,
) -> None:
    created = await _create_ad(fake_uow)

    increment = IncrementAdViews(fake_uow)
    ad = await increment.execute(created.id)

    assert ad.updated_at == created.updated_at


@pytest.mark.asyncio
async def test_increment_views_emits_no_outbox_event(fake_uow: FakeUnitOfWork) -> None:
    created = await _create_ad(fake_uow)

    increment = IncrementAdViews(fake_uow)
    await increment.execute(created.id)

    assert [m.event_type for m in fake_uow.outbox.messages] == ["ad.created"]


@pytest.mark.asyncio
async def test_increment_views_not_found(fake_uow: FakeUnitOfWork) -> None:
    increment = IncrementAdViews(fake_uow)

    with pytest.raises(AdNotFoundError):
        await increment.execute(999)


@pytest.mark.asyncio
async def test_increment_views_on_archived_not_found(fake_uow: FakeUnitOfWork) -> None:
    created = await _create_ad(fake_uow)
    delete = DeleteAd(fake_uow)
    await delete.execute(ad_id=created.id, user_id=1)

    increment = IncrementAdViews(fake_uow)

    with pytest.raises(AdNotFoundError):
        await increment.execute(created.id)

    stored = await fake_uow.ads.get_by_id(created.id)
    assert stored is not None
    assert stored.views == 0
