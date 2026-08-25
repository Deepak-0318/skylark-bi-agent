from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from skylark_bi.agents.monday_agent import MondayConfig
from skylark_bi.agents.monday_agent.client import MondayClient


ME_QUERY = """
query {
  me {
    id
    name
    email
  }
}
"""


def main():
    config = MondayConfig.from_environment()
    client = MondayClient(config)

    data = client.execute(ME_QUERY)

    user = data["me"]

    print("=" * 60)
    print("MONDAY.COM AUTHENTICATION TEST")
    print("=" * 60)
    print(f"Authenticated user : {user['name']}")
    print(f"User ID            : {user['id']}")
    print(f"Email              : {user['email']}")
    print("=" * 60)
    print("AUTHENTICATION SUCCESSFUL")
    print("=" * 60)


if __name__ == "__main__":
    main()