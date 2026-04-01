import requests
import re
from packaging import version
from typedef.konstants import TextStrings



class UpdateChecker:

    def __init__(self):
        self.latest_version = None
        self.current_version = TextStrings.VERSION
        self.release_notes = []
        self.update_available = False

    def check_for_update(self):
        try:
            headers = {
                "Accept": "application/vnd.github+json",
                "User-Agent": "Meile-dVPN-UpdateChecker"
            }
            response = requests.get(TextStrings.GITHUB_API_URL, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            self.latest_version = data.get("tag_name", "").strip()
            body = data.get("body", "")
            self.release_notes = self._parse_whats_new(body, max_items=3)

            current_clean = self._strip_v(self.current_version)
            latest_clean = self._strip_v(self.latest_version)

            if version.parse(latest_clean) > version.parse(current_clean):
                self.update_available = True
                return {
                    "current_version": self.current_version,
                    "latest_version": self.latest_version,
                    "release_notes": self.release_notes,
                    "download_url": TextStrings.DOWNLOAD_URL,
                }

            return None

        except requests.RequestException as e:
            print(f"[UpdateChecker] Network error: {e}")
            return None
        except Exception as e:
            print(f"[UpdateChecker] Error: {e}")
            return None

    @staticmethod
    def _strip_v(version_string: str) -> str:
        return version_string.lstrip("vV")

    @staticmethod
    def _parse_whats_new(body: str, max_items: int = 2) -> list:
        lines = body.split("\n")
        in_whats_new = False
        items = []

        for line in lines:
            stripped = line.strip()

            if re.match(r"^(#{1,6}\s+)?\*{0,2}What'?s\s+New\*{0,2}\s*$",
                        stripped, re.IGNORECASE):
                in_whats_new = True
                continue

            if in_whats_new:
                bullet_match = re.match(r"^[-*]\s+(.+)$", stripped)
                if bullet_match:
                    items.append(bullet_match.group(1).strip())
                    if len(items) >= max_items:
                        break
                elif stripped.startswith("#") or (
                    stripped.startswith("**") and stripped.endswith("**")
                ):
                    break

        return items

def format_update_message(update_info: dict) -> str:
    latest = update_info["latest_version"]
    current = update_info["current_version"]
    notes = update_info["release_notes"]
    url = update_info["download_url"]

    msg = f"Meile dVPN [b]{latest}[/b] is now available!  (You have {current})\n\n"

    if notes:
        msg += "[b]What's New:[/b]\n"
        for note in notes:
            msg += f"  • {note}\n"
        msg += "  & more!\n\n"

    msg += f"Visit [color=#3CDAB7][ref=download]{url}[/ref][/color] to download the latest release."

    return msg