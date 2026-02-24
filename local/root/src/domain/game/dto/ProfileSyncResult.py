from pydantic import BaseModel

from src.domain.game.entities.MissedHeroInventoryData import MissedHeroInventoryData
from src.domain.game.entities.MissedShopsData import MissedShopsData


class ProfileSyncResult(BaseModel):
	shops: 'ProfileSyncShopResult'
	hero_inventory: 'ProfileSyncHeroInventoryResult'


class ProfileSyncShopResult(BaseModel):
	items: int
	spells: int
	units: int
	garrison: int
	missed_data: MissedShopsData | None = None


class ProfileSyncHeroInventoryResult(BaseModel):
	items: int
	missed_data: MissedHeroInventoryData | None = None
