/**
 * Cookie management utility for profile selection persistence
 *
 * Manages cookie storage for default profile selections per game
 * Format: kb_profile_selections=game1_id:profile1_id;game2_id:profile2_id
 */
class CookieManager {

	static COOKIE_NAME = 'kb_profile_selections';

	/**
	 * Get the selected profile ID for a specific game
	 *
	 * :param gameId:
	 *     The game ID to lookup
	 * :return:
	 *     Profile ID if found, null otherwise
	 */
	static getProfileForGame(gameId) {
		const profileMap = this.parseCookie();
		return profileMap[gameId] || null;
	}

	/**
	 * Set the selected profile for a specific game
	 *
	 * :param gameId:
	 *     The game ID
	 * :param profileId:
	 *     The profile ID to associate with the game (null to remove)
	 * :return:
	 */
	static setProfileForGame(gameId, profileId) {
		const profileMap = this.parseCookie();

		if (profileId === null || profileId === '') {
			delete profileMap[gameId];
		} else {
			profileMap[gameId] = profileId;
		}

		const cookieValue = this.serializeCookie(profileMap);
		document.cookie = `${this.COOKIE_NAME}=${cookieValue}; path=/`;
	}

	/**
	 * Parse the cookie string into a map
	 *
	 * :return:
	 *     Object mapping game IDs to profile IDs
	 */
	static parseCookie() {
		const cookies = document.cookie.split(';');
		const profileMap = {};

		for (const cookie of cookies) {
			const trimmed = cookie.trim();
			if (trimmed.startsWith(`${this.COOKIE_NAME}=`)) {
				const value = trimmed.substring(this.COOKIE_NAME.length + 1);
				if (value) {
					const pairs = value.split(';');
					for (const pair of pairs) {
						const [gameId, profileId] = pair.split(':');
						if (gameId && profileId) {
							profileMap[gameId] = profileId;
						}
					}
				}
				break;
			}
		}

		return profileMap;
	}

	/**
	 * Serialize the profile map to cookie format
	 *
	 * :param profileMap:
	 *     Object mapping game IDs to profile IDs
	 * :return:
	 *     Cookie value string
	 */
	static serializeCookie(profileMap) {
		const pairs = [];
		for (const gameId in profileMap) {
			if (profileMap.hasOwnProperty(gameId)) {
				pairs.push(`${gameId}:${profileMap[gameId]}`);
			}
		}
		return pairs.join(';');
	}
}
