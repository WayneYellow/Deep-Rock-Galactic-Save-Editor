import sys
import struct
import json
from typing import Any
from copy import deepcopy
from definitions import (GUID_RE, MAX_BADGES, PROMO_RANKS, RANK_TITLES, RESOURCE_GUIDS,
                                     SEASON_GUID, XP_PER_SEASON_LEVEL,
                                     XP_TABLE)
if sys.platform == "win32":
    import winreg # type: ignore

class QSSLoader:
    def __init__(self):
        pass

    @staticmethod
    def read_qss_file(qss_file_name):
        with open(qss_file_name, 'r',  encoding='UTF-8') as file:
            return file.read()
        
class SaveDataHandler:
    def __init__(self, save_file:bytes):
        self.state = dict()
        self.save_file = save_file
        with open("guids.json", "r") as g:
            self.guid_dict = json.loads(g.read())

    def init_values(self):
        self.state["xp"] = self.get_xp(self.save_file)
        self.state["resources"] = dict()
        self.state["resources"]["credits"] = self.get_credits(self.save_file)
        self.state["resources"]["perks"] = self.get_perk_points(self.save_file)
        resources: dict[str, int] = self.get_resources(self.save_file)
        self.state["resources"]["core"] = resources["core"]
        self.state["resources"]["error"] = resources["error"]
        self.state["resources"]["data"] = resources["data"]
        self.state["resources"]["phazyonite"] = resources["phazyonite"]
        self.state["resources"]["bismor"] = resources["bismor"]
        self.state["resources"]["enor"] = resources["enor"]
        self.state["resources"]["jadiz"] = resources["jadiz"]
        self.state["resources"]["croppa"] = resources["croppa"]
        self.state["resources"]["magnite"] = resources["magnite"]
        self.state["resources"]["umanite"] = resources["umanite"]
        self.state["resources"]["yeast"] = resources["yeast"]
        self.state["resources"]["starch"] = resources["starch"]
        self.state["resources"]["barley"] = resources["barley"]
        self.state["resources"]["malt"] = resources["malt"]
        self.state["season"] = self.get_season_data(self.save_file)
        forged, unacquired, unforged, oc_all = self.get_overclocks()
        self.state["overclocks"] = dict()
        self.state["overclocks"]["forged"] = forged
        self.state["overclocks"]["unacquired"] = unacquired
        self.state["overclocks"]["unforged"] = unforged
        self.state["overclocks"]["all"] = oc_all
        return self.state

    def get_xp(self, save_bytes:bytes):
        # print('getting xp')
        en_marker = b"\x85\xEF\x62\x6C\x65\xF1\x02\x4A\x8D\xFE\xB5\xD0\xF3\x90\x9D\x2E\x03\x00\x00\x00\x58\x50"
        sc_marker = b"\x30\xD8\xEA\x17\xD8\xFB\xBA\x4C\x95\x30\x6D\xE9\x65\x5C\x2F\x8C\x03\x00\x00\x00\x58\x50"
        dr_marker = b"\x9E\xDD\x56\xF1\xEE\xBC\xC5\x48\x8D\x5B\x5E\x5B\x80\xB6\x2D\xB4\x03\x00\x00\x00\x58\x50"
        gu_marker = b"\xAE\x56\xE1\x80\xFE\xC0\xC4\x4D\x96\xFA\x29\xC2\x83\x66\xB9\x7B\x03\x00\x00\x00\x58\x50"

        # start_offset = 0
        xp_offset = 48
        eng_xp_pos: int = save_bytes.find(en_marker) + xp_offset
        scout_xp_pos: int = save_bytes.find(sc_marker) + xp_offset
        drill_xp_pos: int = save_bytes.find(dr_marker) + xp_offset
        gun_xp_pos: int = save_bytes.find(gu_marker) + xp_offset

        eng_xp = struct.unpack("i", save_bytes[eng_xp_pos : eng_xp_pos + 4])[0]
        scout_xp = struct.unpack("i", save_bytes[scout_xp_pos : scout_xp_pos + 4])[0]
        drill_xp = struct.unpack("i", save_bytes[drill_xp_pos : drill_xp_pos + 4])[0]
        gun_xp = struct.unpack("i", save_bytes[gun_xp_pos : gun_xp_pos + 4])[0]

        num_promo_offset = 108
        eng_num_promo = struct.unpack(
            "i",
            save_bytes[eng_xp_pos + num_promo_offset : eng_xp_pos + num_promo_offset + 4],
        )[0]
        scout_num_promo = struct.unpack(
            "i",
            save_bytes[
                scout_xp_pos + num_promo_offset : scout_xp_pos + num_promo_offset + 4
            ],
        )[0]
        drill_num_promo = struct.unpack(
            "i",
            save_bytes[
                drill_xp_pos + num_promo_offset : drill_xp_pos + num_promo_offset + 4
            ],
        )[0]
        gun_num_promo = struct.unpack(
            "i",
            save_bytes[gun_xp_pos + num_promo_offset : gun_xp_pos + num_promo_offset + 4],
        )[0]

        xp_dict: dict[str, dict[str, Any]] = {
            "engineer": {"xp": eng_xp, "promo": eng_num_promo},
            "scout": {"xp": scout_xp, "promo": scout_num_promo},
            "driller": {"xp": drill_xp, "promo": drill_num_promo},
            "gunner": {"xp": gun_xp, "promo": gun_num_promo},
        }
        # pp(xp_dict)
        return xp_dict
    
    def get_season_data(self, save_bytes) -> dict[str, int]:
        # scrip_marker = bytes.fromhex("546F6B656E73")
        season_xp_marker: bytes = bytes.fromhex(SEASON_GUID)
        season_xp_offset = 48
        scrip_offset = 88

        season_xp_pos = save_bytes.find(season_xp_marker) + season_xp_offset
        scrip_pos = save_bytes.find(season_xp_marker) + scrip_offset

        if season_xp_pos == season_xp_offset - 1 and scrip_pos == scrip_offset - 1:
            return {"xp": 0, "scrip": 0}

        season_xp = struct.unpack("i", save_bytes[season_xp_pos : season_xp_pos + 4])[0]
        scrip = struct.unpack("i", save_bytes[scrip_pos : scrip_pos + 4])[0]

        return {"xp": season_xp, "scrip": scrip}
    
    def get_credits(self, save_bytes:bytes):
        marker = b"Credits"
        offset = 33
        pos = save_bytes.find(marker) + offset
        money = struct.unpack("i", save_bytes[pos : pos + 4])[0]

        return money
        
    def get_perk_points(self, save_bytes:bytes):
        marker = b"PerkPoints"
        offset = 36
        if save_bytes.find(marker) == -1:
            perk_points = 0
        else:
            pos = save_bytes.find(marker) + offset
            perk_points = struct.unpack("i", save_bytes[pos : pos + 4])[0]

        return perk_points

    def get_resources(self, save_bytes:bytes):   
        # extracts the resource counts from the save file
        # print('getting resources')
        # resource GUIDs
        resources: dict[str, Any] = deepcopy(RESOURCE_GUIDS)
        guid_length = 16  # length of GUIDs in bytes
        res_marker = (
            b"OwnedResources"  # marks the beginning of where resource values can be found
        )
        res_pos = save_bytes.find(res_marker)
        # print("getting resources")
        for k, v in resources.items():  # iterate through resource list
            # print(f"key: {k}, value: {v}")
            marker = bytes.fromhex(v)
            pos = (
                save_bytes.find(marker, res_pos) + guid_length
            )  # search for the matching GUID
            end_pos = pos + 4  # offset for the actual value
            # extract and unpack the value
            temp = save_bytes[pos:end_pos]
            unp = struct.unpack("f", temp)
            resources[k] = int(unp[0])  # save resource count

        # pp(resources)  # pretty printing for some reason
        return resources
    
    def get_overclocks(self):
        save_bytes = self.save_file
        guid_source = self.guid_dict
        search_term = b"ForgedSchematics"
        search_end = b"SkinFixupCounter"
        pos = save_bytes.find(search_term)
        end_pos = save_bytes.find(search_end)
        if end_pos == -1:
            search_end = b"bFirstSchematicMessageShown"
            end_pos = save_bytes.find(search_end)

        for i in guid_source.values():
            i["status"] = "Unacquired"

        guids = deepcopy(guid_source)
        if pos > 0:
            oc_data = save_bytes[pos:end_pos]
            oc_list_offset = 141

            # print(f'pos: {pos}, end_pos: {end_pos}')
            # print(f'owned_pos: {owned}, diff: {owned-pos}')
            # unforged = True if oc_data.find(b'Owned') else False
            if oc_data.find(b"Owned") > 0:
                unforged = True
            else:
                unforged = False
            # print(unforged) # bool
            num_forged = struct.unpack("i", save_bytes[pos + 63 : pos + 67])[0]
            forged = dict()
            # print(num_forged)

            for i in range(num_forged):
                uuid = (
                    save_bytes[
                        pos
                        + oc_list_offset
                        + (i * 16) : pos
                        + oc_list_offset
                        + (i * 16)
                        + 16
                    ]
                    .hex()
                    .upper()
                )
                try:
                    a = guids[uuid]
                    guid_source[uuid]["status"] = "Forged"
                    a["status"] = "Forged"
                    del guids[uuid]
                    forged.update({uuid: a})

                    # print('success')
                except Exception as e:
                    # print(f'Error: {e}')
                    pass

            #print('after forged extraction')
            if unforged:
                unforged = dict()
                #print('in unforged loop')
                num_pos = save_bytes.find(b"Owned", pos) + 62
                num_unforged = struct.unpack("i", save_bytes[num_pos : num_pos + 4])[0]
                unforged_pos = num_pos + 77
                for i in range(num_unforged):
                    uuid = (
                        save_bytes[unforged_pos + (i * 16) : unforged_pos + (i * 16) + 16]
                        .hex()
                        .upper()
                    )
                    try:
                        unforged.update({uuid: guids[uuid]})
                        guid_source[uuid]["status"] = "Unforged"
                        unforged[uuid]["status"] = "Unforged"
                    except KeyError:
                        unforged.update({uuid: "Cosmetic"})
            else:
                unforged = dict()
        else:
            forged = dict()
            unforged = dict()

        #print('after unforged extraction')
        # print(f'unforged: {unforged}')
        # forged OCs, unacquired OCs, unforged OCs
        return (forged, guids, unforged, guid_source)
    
    def save_changes(self, changes: dict[str, Any], file_name) -> None:
        save_file: bytes = self.make_save_file(changes)
        with open(file_name, "wb") as f:
            f.write(save_file)

    def make_save_file(self, change_data) -> bytes:
        new_values = change_data
        save_data = self.save_file
        # write resources
        # resource_bytes = list()
        # res_guids = deepcopy(resource_guids)
        resources: dict[str, int] = {
            "yeast": new_values["resources"]["yeast"],
            "starch": new_values["resources"]["starch"],
            "barley": new_values["resources"]["barley"],
            "bismor": new_values["resources"]["bismor"],
            "enor": new_values["resources"]["enor"],
            "malt": new_values["resources"]["malt"],
            "umanite": new_values["resources"]["umanite"],
            "jadiz": new_values["resources"]["jadiz"],
            "croppa": new_values["resources"]["croppa"],
            "magnite": new_values["resources"]["magnite"],
            "error": new_values["resources"]["error"],
            "core": new_values["resources"]["core"],
            "data": new_values["resources"]["data"],
            "phazyonite": new_values["resources"]["phazyonite"],
        }

        res_marker = b"OwnedResources"
        res_pos: int = save_data.find(res_marker) + 85
        res_length = struct.unpack("i", save_data[res_pos - 4 : res_pos])[0] * 20
        res_bytes: bytes = save_data[res_pos : res_pos + res_length]

        for k, v in resources.items():
            if res_bytes.find(bytes.fromhex(RESOURCE_GUIDS[k])) > -1:
                pos: int = res_bytes.find(bytes.fromhex(RESOURCE_GUIDS[k]))
                res_bytes = (
                    res_bytes[: pos + 16] + struct.pack("f", v) + res_bytes[pos + 20 :]
                )
                # print(
                #     f'res: {k}, pos: {pos}, guid: {res_guids[k]}, val: {v}, v bytes: {struct.pack("f", v)}'
                # )

        # print(res_bytes.hex().upper())

        save_data = save_data[:res_pos] + res_bytes + save_data[res_pos + res_length :]

        # write credits
        cred_marker = b"Credits"
        cred_pos: int = save_data.find(cred_marker) + 33
        cred_bytes: bytes = struct.pack("i", new_values["resources"]["credits"])
        save_data = save_data[:cred_pos] + cred_bytes + save_data[cred_pos + 4 :]

        # write perk points
        if new_values["resources"]["perks"] > 0:
            perks_marker = b"PerkPoints"
            perks_bytes: bytes = struct.pack("i", new_values["resources"]["perks"])
            if save_data.find(perks_marker) != -1:
                perks_pos: int = save_data.find(perks_marker) + 36
                save_data = save_data[:perks_pos] + perks_bytes + save_data[perks_pos + 4 :]
            else:
                perks_entry: bytes = (
                    b"\x0B\x00\x00\x00\x50\x65\x72\x6B\x50\x6F\x69\x6E\x74\x73\x00\x0C\x00\x00\x00\x49\x6E\x74\x50\x72\x6F\x70\x65\x72\x74\x79\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00"
                    + perks_bytes
                )
                perks_pos = save_data.find(
                    b"\x11\x00\x00\x00\x55\x6E\x4C\x6F\x63\x6B\x65\x64\x4D\x69\x73\x73\x69\x6F\x6E\x73\x00\x0E"
                )
                save_data = (
                    save_data[:perks_pos] + perks_entry + save_data[perks_pos:]
                )  # inserting data, not overwriting
        # print(f'2. {len(save_data)}')
        # write XP
        en_marker = b"\x85\xEF\x62\x6C\x65\xF1\x02\x4A\x8D\xFE\xB5\xD0\xF3\x90\x9D\x2E\x03\x00\x00\x00\x58\x50"
        sc_marker = b"\x30\xD8\xEA\x17\xD8\xFB\xBA\x4C\x95\x30\x6D\xE9\x65\x5C\x2F\x8C\x03\x00\x00\x00\x58\x50"
        dr_marker = b"\x9E\xDD\x56\xF1\xEE\xBC\xC5\x48\x8D\x5B\x5E\x5B\x80\xB6\x2D\xB4\x03\x00\x00\x00\x58\x50"
        gu_marker = b"\xAE\x56\xE1\x80\xFE\xC0\xC4\x4D\x96\xFA\x29\xC2\x83\x66\xB9\x7B\x03\x00\x00\x00\x58\x50"
        offset = 48
        eng_xp_pos: int = save_data.find(en_marker) + offset
        scout_xp_pos: int = save_data.find(sc_marker) + offset
        drill_xp_pos: int = save_data.find(dr_marker) + offset
        gun_xp_pos: int = save_data.find(gu_marker) + offset

        eng_xp_bytes: bytes = struct.pack("i", new_values["xp"]["engineer"]["xp"])
        scout_xp_bytes: bytes = struct.pack("i", new_values["xp"]["scout"]["xp"])
        drill_xp_bytes: bytes = struct.pack("i", new_values["xp"]["driller"]["xp"])
        gun_xp_bytes: bytes = struct.pack("i", new_values["xp"]["gunner"]["xp"])

        promo_offset = 108
        levels_per_promo = 25
        promo_levels_offset = 56
        eng_promo_pos: int = eng_xp_pos + promo_offset
        scout_promo_pos: int = scout_xp_pos + promo_offset
        drill_promo_pos: int = drill_xp_pos + promo_offset
        gun_promo_pos: int = gun_xp_pos + promo_offset

        eng_promo_bytes: bytes = struct.pack("i", new_values["xp"]["engineer"]["promo"])
        eng_promo_level_bytes: bytes = struct.pack(
            "i", new_values["xp"]["engineer"]["promo"] * levels_per_promo
        )
        scout_promo_bytes: bytes = struct.pack("i", new_values["xp"]["scout"]["promo"])
        scout_promo_level_bytes: bytes = struct.pack(
            "i", new_values["xp"]["scout"]["promo"] * levels_per_promo
        )
        drill_promo_bytes: bytes = struct.pack("i", new_values["xp"]["driller"]["promo"])
        drill_promo_level_bytes: bytes = struct.pack(
            "i", new_values["xp"]["driller"]["promo"] * levels_per_promo
        )
        gun_promo_bytes: bytes = struct.pack("i", new_values["xp"]["gunner"]["promo"])
        gun_promo_level_bytes: bytes = struct.pack(
            "i", new_values["xp"]["gunner"]["promo"] * levels_per_promo
        )

        save_data = save_data[:eng_xp_pos] + eng_xp_bytes + save_data[eng_xp_pos + 4 :]
        save_data = (
            save_data[:eng_promo_pos] + eng_promo_bytes + save_data[eng_promo_pos + 4 :]
        )
        save_data = (
            save_data[: eng_promo_pos + promo_levels_offset]
            + eng_promo_level_bytes
            + save_data[eng_promo_pos + promo_levels_offset + 4 :]
        )

        save_data = (
            save_data[:scout_xp_pos] + scout_xp_bytes + save_data[scout_xp_pos + 4 :]
        )
        save_data = (
            save_data[:scout_promo_pos]
            + scout_promo_bytes
            + save_data[scout_promo_pos + 4 :]
        )
        save_data = (
            save_data[: scout_promo_pos + promo_levels_offset]
            + scout_promo_level_bytes
            + save_data[scout_promo_pos + promo_levels_offset + 4 :]
        )

        save_data = (
            save_data[:drill_xp_pos] + drill_xp_bytes + save_data[drill_xp_pos + 4 :]
        )
        save_data = (
            save_data[:drill_promo_pos]
            + drill_promo_bytes
            + save_data[drill_promo_pos + 4 :]
        )
        save_data = (
            save_data[: drill_promo_pos + promo_levels_offset]
            + drill_promo_level_bytes
            + save_data[drill_promo_pos + promo_levels_offset + 4 :]
        )

        save_data = save_data[:gun_xp_pos] + gun_xp_bytes + save_data[gun_xp_pos + 4 :]
        save_data = (
            save_data[:gun_promo_pos] + gun_promo_bytes + save_data[gun_promo_pos + 4 :]
        )
        save_data = (
            save_data[: gun_promo_pos + promo_levels_offset]
            + gun_promo_level_bytes
            + save_data[gun_promo_pos + promo_levels_offset + 4 :]
        )
        # print(f'3. {len(save_data)}')
        # write overclocks
        search_term = b"ForgedSchematics"  # \x00\x0F\x00\x00\x00Struct'
        search_end = b"SkinFixupCounter"
        pos = save_data.find(search_term)
        end_pos: int = (
            save_data.find(search_end) - 4
        )  # means I don't have to hardcode the boundary bytes
        # print(f'pos: {pos}, end_pos: {end_pos}')

        # # this is currently broken, don't care enough to put more effort into fixing it.
        # # the problem seems to be related to the \x5D in the middle of the first hex string,
        # # this changes to \x6D when going from 1->2 overclocks. Similarly, the \x10 in the
        # # middle of the second hex string (\x74\x79\x00\x10 <- this one) changes to \x20
        # # when going from 1->2 overclocks. My testing involved one weapon OC and one cosmetic OC.
        # # If someone can provide a save file with more than 2 overclocks waiting to be forged,
        # # that might help figure it out, but I'm currently stumped.
        if pos > 0:
            num_forged = struct.unpack("i", save_data[pos + 63 : pos + 67])[0]
            unforged_ocs = new_values['overclocks']["unforged"]

            schematic_save_marker = b"SchematicSave"
            schematic_save_offset = 33
            schematic_save_pos = save_data.find(schematic_save_marker) + schematic_save_offset
            schematic_save_end_pos = schematic_save_pos + 8
            schematic_save_size = b""

            if len(unforged_ocs) > 0:
                ocs: bytes = (
                    b"\x10\x00\x00\x00\x4F\x77\x6E\x65\x64\x53\x63\x68\x65\x6D\x61\x74\x69\x63\x73\x00\x0E\x00\x00\x00\x41\x72\x72\x61\x79\x50\x72\x6F\x70\x65\x72\x74\x79\x00"
                    # number of bytes between position of first "OwnedSchematic" and end_pos, -62, as a 64bit unsigned integer
                    + struct.pack("Q", 139 + len(unforged_ocs)*16 - 62)
                    + b"\x0F\x00\x00\x00\x53\x74\x72\x75\x63\x74\x50\x72\x6F\x70\x65\x72\x74\x79\x00\x00"
                    # number of unforged ocs, stored as a 32bit unsigned integer
                    + struct.pack("I", len(unforged_ocs))

                    + b"\x10\x00\x00\x00\x4F\x77\x6E\x65\x64\x53\x63\x68\x65\x6D\x61\x74\x69\x63\x73\x00\x0F\x00\x00\x00\x53\x74\x72\x75\x63\x74\x50\x72\x6F\x70\x65\x72\x74\x79\x00"
                    # number of bytes taken up by the GUID's of the unforged oc's, stored as a 64bit unsigned integer
                    + struct.pack("Q", len(unforged_ocs)*16)
                    + b"\x05\x00\x00\x00\x47\x75\x69\x64\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                )
                #print(ocs)
                uuids: list[bytes] = [bytes.fromhex(i) for i in unforged_ocs.keys()]
                for i in uuids:
                    ocs += i

                # the number of bytes between position of first "SchematicSave" and end_pos, -17, as a 64bit unsigned integer
                schematic_save_size = struct.pack("Q", 139 + (141 + num_forged*16) + 4 + (139 + len(unforged_ocs)*16) - 17 )

            else:
                ocs = b""
                # the number of bytes between position of first "SchematicSave" and end_pos, -17, as a 64bit unsigned integer
                schematic_save_size = struct.pack("Q", 139 + (141 + num_forged*16) - 17 )

            save_data = (
                save_data[: pos + (num_forged * 16) + 141] + ocs + save_data[end_pos:]
            )
            save_data = (
                save_data[:schematic_save_pos] + schematic_save_size + save_data[schematic_save_end_pos:]
            )

        # write season data
        season_xp_marker: bytes = bytes.fromhex(SEASON_GUID)
        season_xp_offset = 48
        season_xp_pos: int = save_data.find(season_xp_marker) + season_xp_offset
        # scrip_marker = b"Tokens"
        scrip_offset = 88
        scrip_pos: int = save_data.find(season_xp_marker) + scrip_offset

        save_data = (
            save_data[:season_xp_pos]
            + struct.pack("i", new_values["season"]["xp"])
            + save_data[season_xp_pos + 4 :]
        )
        save_data = (
            save_data[:scrip_pos]
            + struct.pack("i", new_values["season"]["scrip"])
            + save_data[scrip_pos + 4 :]
        )

        return save_data
    


def findSteamPath():
    try:
        steam_path = "."
        if sys.platform == "win32":
            steam_reg = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") # type: ignore
            steam_path = winreg.QueryValueEx(steam_reg, "SteamPath")[0] # type: ignore
            steam_path += "/steamapps/common/Deep Rock Galactic/FSD/Saved/SaveGames"
        else:
            steam_path = "."
    except:
            steam_path = "."
    return steam_path

def load_save_file(file_name):
    with open(file_name, "rb") as f:
        save_file = f.read()
    # make a backup of the save file in case of weirdness or bugs
    with open(f"{file_name}.old", "wb") as backup:
        backup.write(save_file)
    return save_file

