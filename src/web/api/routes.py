from fastapi import APIRouter, HTTPException, Depends
from dependency_injector.wiring import inject, Provide
from src.web.api.models import AddShopToItemRequest, UpdateShopCountRequest
from src.domain.game.services.ItemService import ItemService
from src.domain.game.IProfileService import IProfileService
from src.domain.game.ISaveFileService import ISaveFileService
from src.domain.game.IGameService import IGameService
from src.web.dependencies.game_context import get_game_context, GameContext
from src.domain.game.repositories.CrudRepository import _game_context


router = APIRouter(prefix="/api", tags=["api"])


@router.get("/games/{game_id}/profiles/{profile_id}/tracked")
@inject
async def get_tracked_items(
	game_id: int,
	profile_id: int,
	game_context: GameContext = Depends(get_game_context),
	item_tracking_service: ItemService = Depends(Provide["item_tracking_service"]),
	profile_service: IProfileService = Depends(Provide["profile_service"])
):
	"""
	Get all items with tracked shops for a profile

	:param game_id:
		Game ID
	:param profile_id:
		Profile ID
	:param game_context:
		Game context with schema information
	:param item_tracking_service:
		Item tracking service
	:param profile_service:
		Profile service
	:return:
		List of items with tracked shops
	"""
	_game_context.set(game_context)

	profile = profile_service.get_profile(profile_id)
	if not profile:
		raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")

	items_data = item_tracking_service.get_all_items_with_tracked_shops(profile_id=profile_id)

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


@router.post("/games/{game_id}/profiles/{profile_id}/items/{item_id}/shops")
@inject
async def add_shop_to_item(
	game_id: int,
	profile_id: int,
	item_id: int,
	request_data: AddShopToItemRequest,
	game_context: GameContext = Depends(get_game_context),
	item_tracking_service: ItemService = Depends(Provide["item_tracking_service"]),
	profile_service: IProfileService = Depends(Provide["profile_service"])
):
	"""
	Add shop tracking to an item

	:param game_id:
		Game ID
	:param profile_id:
		Profile ID
	:param item_id:
		Item ID
	:param request_data:
		Request data with shop_id and count
	:param game_context:
		Game context with schema information
	:param item_tracking_service:
		Item tracking service
	:param profile_service:
		Profile service
	:return:
		Success message
	"""
	_game_context.set(game_context)

	profile = profile_service.get_profile(profile_id)
	if not profile:
		raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")

	item_tracking_service.link_item_to_shop(
		profile_id=profile_id,
		item_id=item_id,
		shop_id=request_data.shop_id,
		count=request_data.count
	)
	return {"message": "Shop added successfully"}


@router.patch("/games/{game_id}/profiles/{profile_id}/items/{item_id}/shops/{shop_id}")
@inject
async def update_shop_count(
	game_id: int,
	profile_id: int,
	item_id: int,
	shop_id: int,
	request_data: UpdateShopCountRequest,
	game_context: GameContext = Depends(get_game_context),
	item_tracking_service: ItemService = Depends(Provide["item_tracking_service"]),
	profile_service: IProfileService = Depends(Provide["profile_service"])
):
	"""
	Update quantity for item-shop tracking

	:param game_id:
		Game ID
	:param profile_id:
		Profile ID
	:param item_id:
		Item ID
	:param shop_id:
		Shop ID
	:param request_data:
		Request data with new count
	:param game_context:
		Game context with schema information
	:param item_tracking_service:
		Item tracking service
	:param profile_service:
		Profile service
	:return:
		Success message
	"""
	_game_context.set(game_context)

	profile = profile_service.get_profile(profile_id)
	if not profile:
		raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")

	item_tracking_service.update_item_shop_count(
		profile_id=profile_id,
		item_id=item_id,
		shop_id=shop_id,
		count=request_data.count
	)
	return {"message": "Count updated successfully"}


@router.delete("/games/{game_id}/profiles/{profile_id}/items/{item_id}/shops/{shop_id}")
@inject
async def remove_shop_from_item(
	game_id: int,
	profile_id: int,
	item_id: int,
	shop_id: int,
	game_context: GameContext = Depends(get_game_context),
	item_tracking_service: ItemService = Depends(Provide["item_tracking_service"]),
	profile_service: IProfileService = Depends(Provide["profile_service"])
):
	"""
	Remove shop tracking from an item

	:param game_id:
		Game ID
	:param profile_id:
		Profile ID
	:param item_id:
		Item ID
	:param shop_id:
		Shop ID
	:param game_context:
		Game context with schema information
	:param item_tracking_service:
		Item tracking service
	:param profile_service:
		Profile service
	:return:
		Success message
	"""
	_game_context.set(game_context)

	profile = profile_service.get_profile(profile_id)
	if not profile:
		raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")

	item_tracking_service.remove_item_from_shop(
		profile_id=profile_id,
		item_id=item_id,
		shop_id=shop_id
	)
	return {"message": "Shop removed successfully"}


@router.get("/games/{game_id}/shops-grouped")
@inject
async def get_shops_grouped_by_location(
	game_id: int,
	game_context: GameContext = Depends(get_game_context),
	item_tracking_service: ItemService = Depends(Provide["item_tracking_service"])
):
	"""
	Get shops grouped by location for dropdown

	:param game_id:
		Game ID
	:param game_context:
		Game context with schema information
	:param item_tracking_service:
		Item tracking service
	:return:
		Shops grouped by location
	"""
	_game_context.set(game_context)

	groups = item_tracking_service.get_shops_grouped_by_location()

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


@router.get("/games/{game_id}/save-directories")
@inject
async def list_save_directories(
	game_id: int,
	game_context: GameContext = Depends(get_game_context),
	save_file_service: ISaveFileService = Depends(Provide["save_file_service"]),
	game_service: IGameService = Depends(Provide["game_service"])
):
	"""
	List available save directories for a game

	:param game_id:
		Game ID
	:param game_context:
		Game context
	:param save_file_service:
		Save file service
	:param game_service:
		Game service
	:return:
		Save directories grouped by game name
	"""
	_game_context.set(game_context)

	game = game_service.get_game(game_id)
	if not game:
		raise HTTPException(status_code=404, detail="Game not found")

	try:
		save_dirs = save_file_service.list_save_directories(game.path, limit=100)
		return save_dirs
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to list saves: {str(e)}")


@router.post("/games/{game_id}/scan-save")
@inject
async def scan_save_file(
	game_id: int,
	request_data: dict,
	game_context: GameContext = Depends(get_game_context),
	save_file_service: ISaveFileService = Depends(Provide["save_file_service"]),
	game_service: IGameService = Depends(Provide["game_service"])
):
	"""
	Scan a save file and extract campaign data

	:param game_id:
		Game ID
	:param request_data:
		Request data with save_dir key
	:param game_context:
		Game context
	:param save_file_service:
		Save file service
	:param game_service:
		Game service
	:return:
		Campaign data
	"""
	_game_context.set(game_context)

	game = game_service.get_game(game_id)
	if not game:
		raise HTTPException(status_code=404, detail="Game not found")

	save_dir = request_data.get("save_dir")
	if not save_dir:
		raise HTTPException(status_code=400, detail="save_dir is required")

	try:
		campaign_data = save_file_service.scan_save_file(game.path, save_dir)
		return campaign_data
	except FileNotFoundError as e:
		raise HTTPException(status_code=404, detail=str(e))
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")
