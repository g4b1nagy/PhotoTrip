def bytes_to_human_readable(size):
    for unit in ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]:
        if size < 1024:
            return "{:.2f} {}".format(size, unit)
        size /= 1024
    return "{:.2f} {}".format(size, "YB")
