from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    ACTIVE_SESSIONS: int = Field(
        default=1,
        description="Number of parallel running processes (Chrome session instances). Each session requires ~500 MB RAM"
    )

    VERIFY_PROXY: bool = Field(
        default=False,
        description="Visit a website to check the IP address. The IP address from the website and provided proxy IP address must be the same."
    )

    TIMEOUT: int = Field(
        default=30,
        description="Timeout in seconds used in Chrome Driver to wait for the page to load, find html elements, etc. \
            (First run takes more time to load)"
    )
    
    CHROME_DRIVER_PATH: Optional[str] = None # None(=downloads and patches new binary)
    CHROME_PATH: Optional[str] = None # If not specified, make sure the executable's folder is in $PATH
    
    DISABLE_WEBRTC: bool = Field(
        default=False,
        description="When using a proxy, your real IP address may be exposed through WebRTC. To prevent this in Google Chrome, you must use an extension that disables WebRTC. (Recommended option is 'True')"
    )
    WEBRTC_EXTENSION_PATH: Optional[str] = Field(
        default=None,
        description="Mandatory if DISABLE_WEBRTC is True. Full path to the extension (unpacked) that disables webrtc. In Chrome WebRTC cannot be turned off using default options."
    )
    
    HEADLESS: bool = True # True - start Chrome headless (without UI). False - start with UI.
    
    DEBUG_MODE: bool = False # For development purposes

settings = Settings()