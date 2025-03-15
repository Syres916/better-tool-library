import os
import FreeCAD

from PySide import QtCore, QtGui, QtSvg, __version__ as pyside_version

try:
    import FreeCADGui
    load_ui = FreeCADGui.PySideUic.loadUi
except ImportError:
    try:
        from PySide6.QtUiTools import QUiLoader
    except ImportError:
        from PySide2.QtUiTools import QUiLoader
    def load_ui(ui_path, parent=None, custom_widgets=None):
        dir_path = os.path.dirname(__file__)
        q_ui_file = QtCore.QFile(ui_path)
        q_ui_file.open(QtCore.QFile.OpenModeFlag.ReadOnly)
        loader = QUiLoader()
        if hasattr(QtCore, "QDir"):
            loader.setWorkingDirectory(QtCore.QDir(dir_path)) #Qt6
        else:
            loader.setWorkingDirectory(dir_path) #Qt5
        if custom_widgets:
            for widget in custom_widgets:
                loader.registerCustomWidget(widget)
        form = loader.load(ui_path)
        q_ui_file.close()
        return form

from pip._internal.metadata import pkg_resources

default_lib_path = os.path.join("~", ".btl", "Library")

def get_library_path():
    prefs = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/CAM")
    if not prefs.IsEmpty():
        return prefs.GetString("LastPathToolLibrary", default_lib_path)
    return get_old_library_path()

def get_old_library_path():
    prefs = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Path")
    return prefs.GetString("LastPathToolLibrary", default_lib_path)

def get_library_path_list():
    """
    Returns a list of possible paths in order of priority.
    """
    paths = [get_library_path(), get_old_library_path(), default_lib_path]
    return list(dict.fromkeys(paths)) # Remove duplicates while preserving priority order

def set_library_path(path):
    prefs = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/CAM")
    if not prefs.IsEmpty():
        return prefs.SetString("LastPathToolLibrary", path)
    prefs = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Path")
    return prefs.SetString("LastPathToolLibrary", path)

def qpixmap_from_png(byte_array, icon_size, ratio=1.0):
    render_size = QtCore.QSize(icon_size.width()*ratio, icon_size.height()*ratio)
    pixmap = QtGui.QPixmap(render_size)
    pixmap.fill(QtGui.Qt.transparent)
    pixmap.loadFromData(byte_array)
    return pixmap.scaled(icon_size, QtCore.Qt.KeepAspectRatio)

def qpixmap_from_svg(byte_array, icon_size, ratio=1.0):
    render_size = QtCore.QSize(icon_size.width()*ratio, icon_size.height()*ratio)

    image = QtGui.QImage(render_size, QtGui.QImage.Format_ARGB32)
    image.fill(QtGui.Qt.transparent)
    painter = QtGui.QPainter(image)

    if pkg_resources.parse_version(pyside_version) >= pkg_resources.parse_version("6.0.0"):
        buffer = QtCore.QBuffer(byte_array)  # PySide6
        buffer.open(QtCore.QIODevice.ReadOnly)
        data = QtCore.QXmlStreamReader(buffer)
    else:
        data = QtCore.QXmlStreamReader(byte_array.data())  # PySide5
    renderer = QtSvg.QSvgRenderer(data)
    renderer.setAspectRatioMode(QtCore.Qt.KeepAspectRatio)
    renderer.render(painter)
    painter.end()

    return QtGui.QPixmap.fromImage(image)

def get_pixmap_from_shape(shape, size, ratio):
    icon_type, icon_bytes = shape.get_icon()
    if not icon_type:
        return None
    icon_ba = QtCore.QByteArray(icon_bytes)

    if icon_type == 'svg':
        return qpixmap_from_svg(icon_ba, size, ratio)
    elif icon_type == 'png':
        return qpixmap_from_png(icon_ba, size, ratio)

    return None
