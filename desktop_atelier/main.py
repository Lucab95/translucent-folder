from .app import DesktopAtelierApplication


def main() -> int:
    app = DesktopAtelierApplication()
    return app.run(None)


if __name__ == '__main__':
    raise SystemExit(main())
