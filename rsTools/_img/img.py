import maya.app.general.resourceBrowser as resourceBrowser


def showIcons():
    resource_browser = resourceBrowser.resourceBrowser().run()
    resource_path = resource_browser.run()
    return resource_path


if __name__ == "__main__":
    resource_path = showIcons()
    if resource_path:
        print(resource_path)
