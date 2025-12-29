from fastapi import APIRouter, HTTPException, Depends
from dependency_injector.wiring import inject, Provide
from src.web.api.models import AddShopToItemRequest, UpdateShopCountRequest
from src.domain.game.services.ItemTrackingService import ItemTrackingService
from src.domain.profile.IProfileService import IProfileService
from src.domain.exceptions import EntityNotFoundException, DuplicateEntityException


router = APIRouter(prefix="/api", tags=["api"])


@router.get("/profiles/{profile_id}/tracked")
@inject
async def get_tracked_items(
	profile_id: int,
	item_tracking_service: ItemTrackingService = Depends(Provide["item_tracking_service"]),
	profile_service: IProfileService = Depends(Provide["profile_service"])
):
	"""
	Get all items with tracked shops for a profile

	:param profile_id:
		Profile ID
	:param item_tracking_service:
		Item tracking service
	:param profile_service:
		Profile service
	:return:
		List of items with tracked shops
	"""
	profile = profile_service.get_profile(profile_id)
	if not profile:
		raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")

	items_data = item_tracking_service.get_all_items_with_tracked_shops(
		profile_id=profile_id,
		game_id=profile.game_id
	)

	result = []
	for item_data in items_data:
		item_dict = {
			"id": item_data["item"].id,
			"name": item_data["item"].name,
			"price": item_data["item"].price,
			"hint": item_data["item"].hint
		}

		tracked_shops = []
		for ts in item_data["tracked_shops"]:
			shop_dict = {
				"shop_id": ts["shop"].id if ts["shop"] else None,
				"shop_name": ts["shop"].name if ts["shop"] else "Unknown",
				"location_id": ts["location"].id if ts["location"] else None,
				"location_name": ts["location"].name if ts["location"] else "Unknown",
				"count": ts["count"]
			}
			tracked_shops.append(shop_dict)

		result.append({
			"item": item_dict,
			"tracked_shops": tracked_shops
		})

	return result


@router.post("/profiles/{profile_id}/items/{item_id}/shops")
@inject
async def add_shop_to_item(
	profile_id: int,
	item_id: int,
	request_data: AddShopToItemRequest,
	item_tracking_service: ItemTrackingService = Depends(Provide["item_tracking_service"]),
	profile_service: IProfileService = Depends(Provide["profile_service"])
):
	"""
	Add shop tracking to an item

	:param profile_id:
		Profile ID
	:param item_id:
		Item ID
	:param request_data:
		Request data with shop_id and count
	:param item_tracking_service:
		Item tracking service
	:param profile_service:
		Profile service
	:return:
		Success message
	"""
	profile = profile_service.get_profile(profile_id)
	if not profile:
		raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")

	try:
		item_tracking_service.link_item_to_shop(
			profile_id=profile_id,
			item_id=item_id,
			shop_id=request_data.shop_id,
			count=request_data.count
		)
		return {"message": "Shop added successfully"}
	except DuplicateEntityException as e:
		raise HTTPException(status_code=409, detail=str(e))
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.patch("/profiles/{profile_id}/items/{item_id}/shops/{shop_id}")
@inject
async def update_shop_count(
	profile_id: int,
	item_id: int,
	shop_id: int,
	request_data: UpdateShopCountRequest,
	item_tracking_service: ItemTrackingService = Depends(Provide["item_tracking_service"]),
	profile_service: IProfileService = Depends(Provide["profile_service"])
):
	"""
	Update quantity for item-shop tracking

	:param profile_id:
		Profile ID
	:param item_id:
		Item ID
	:param shop_id:
		Shop ID
	:param request_data:
		Request data with new count
	:param item_tracking_service:
		Item tracking service
	:param profile_service:
		Profile service
	:return:
		Success message
	"""
	profile = profile_service.get_profile(profile_id)
	if not profile:
		raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")

	try:
		item_tracking_service.update_item_shop_count(
			profile_id=profile_id,
			item_id=item_id,
			shop_id=shop_id,
			count=request_data.count
		)
		return {"message": "Count updated successfully"}
	except EntityNotFoundException as e:
		raise HTTPException(status_code=404, detail=str(e))
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.delete("/profiles/{profile_id}/items/{item_id}/shops/{shop_id}")
@inject
async def remove_shop_from_item(
	profile_id: int,
	item_id: int,
	shop_id: int,
	item_tracking_service: ItemTrackingService = Depends(Provide["item_tracking_service"]),
	profile_service: IProfileService = Depends(Provide["profile_service"])
):
	"""
	Remove shop tracking from an item

	:param profile_id:
		Profile ID
	:param item_id:
		Item ID
	:param shop_id:
		Shop ID
	:param item_tracking_service:
		Item tracking service
	:param profile_service:
		Profile service
	:return:
		Success message
	"""
	profile = profile_service.get_profile(profile_id)
	if not profile:
		raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")

	try:
		item_tracking_service.remove_item_from_shop(
			profile_id=profile_id,
			item_id=item_id,
			shop_id=shop_id
		)
		return {"message": "Shop removed successfully"}
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.get("/games/{game_id}/shops-grouped")
@inject
async def get_shops_grouped_by_location(
	game_id: int,
	item_tracking_service: ItemTrackingService = Depends(Provide["item_tracking_service"])
):
	"""
	Get shops grouped by location for dropdown

	:param game_id:
		Game ID
	:param item_tracking_service:
		Item tracking service
	:return:
		Shops grouped by location
	"""
	groups = item_tracking_service.get_shops_grouped_by_location(game_id)

	result = []
	for group in groups:
		location_dict = {
			"id": group["location"].id,
			"name": group["location"].name
		}

		shops_list = []
		for shop in group["shops"]:
			shop_dict = {
				"id": shop.id,
				"name": shop.name,
				"hint": shop.hint
			}
			shops_list.append(shop_dict)

		result.append({
			"location": location_dict,
			"shops": shops_list
		})

	return result
