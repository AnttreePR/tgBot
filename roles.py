"""Role definitions and user management for the Telegram bot.

This module defines available roles and associates specific Telegram user
identifiers with those roles. It also exposes a helper function to
determine a user's role based on their Telegram ID. If a user is not
registered in the system, they default to the CUSTOMER role.

Attributes:
    OWNER (str): Role with full administrative privileges.
    OPERATOR (str): Role with limited administrative privileges.
    CUSTOMER (str): Role with access to customer‑facing features.
    USERS (dict[int, str]): Mapping of Telegram user IDs to roles.

Functions:
    get_role(user_id: int) -> str: Returns the role associated with a given
        Telegram user ID or the default CUSTOMER role if not found.
"""

from typing import Dict

# Define role constants for clarity and to avoid typos across the project.
OWNER: str = "OWNER"
OPERATOR: str = "OPERATOR"
CUSTOMER: str = "CUSTOMER"

# Mapping of Telegram user IDs to their roles. If a user is not listed here,
# they will be treated as a CUSTOMER. Populate this dictionary with your
# known operators or owners. The example below marks a specific user ID as
# the OWNER; replace or extend as needed.
USERS: Dict[int, str] = {
    936_977_024: OWNER,  # Primary owner ID provided in the project description
    # Add additional user_id: role pairs here
}

def get_role(user_id: int) -> str:
    """Return the role for a given Telegram user ID.

    Args:
        user_id (int): Telegram user identifier.

    Returns:
        str: The role associated with the user. Defaults to CUSTOMER if
            the user is not present in the USERS dictionary.
    """
    return USERS.get(user_id, CUSTOMER)
