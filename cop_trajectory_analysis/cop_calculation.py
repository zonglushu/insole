import numpy as np


# 根据左侧鞋垫所在最小矩形左上角坐标生成左侧鞋垫传感器坐标
def left_map_rule(rectangle_left_top_xy: list, rectangle_width_hight: list, left_xy:dict)->None:
    """
    rectangle_left_top_xy:左上角坐标
    rectangle_width_hight:宽高
    """

    interval = 1
    x1, y1 = rectangle_left_top_xy
    w, h = rectangle_width_hight
    # 计算前脚掌坐标
    frontend_xy = (x1 + 3 * interval, y1 - 4 * interval)
    C3 = frontend_xy
    C2 = (frontend_xy[0] + interval, frontend_xy[1])
    C1 = (frontend_xy[0] + 2 * interval, frontend_xy[1])
    C11 = (frontend_xy[0], frontend_xy[1] - interval)
    C10 = (frontend_xy[0] + interval, frontend_xy[1] - interval)
    C9 = (frontend_xy[0] + 2 * interval, frontend_xy[1] - interval)
    # 前脚掌坐标列表
    frontend_xy = [C1, C2, C3, C9, C10, C11]
    # 计算中脚掌坐标
    C12 = (C11[0], C11[1] - interval)
    C4 = (C12[0] - interval, C12[1])
    C13 = (C11[0], C11[1] - 2 * interval)
    C5 = (C4[0], C4[1] - interval)
    C14 = (C11[0], C11[1] - 3 * interval)
    C6 = (C5[0], C5[1] - interval)
    # 中脚掌坐标
    center_xy = [C12, C4, C13, C5, C14, C5]

    # 计算后脚掌坐标
    C7 = (C14[0], C14[1] - interval)
    C8 = (C14[0], C14[1] - 2 * interval)
    C15 = (C7[0] + interval, C7[1])
    C16 = (C15[0], C15[1] - interval)
    # 后脚掌坐标
    backend_xy = [C15, C7, C16, C8]

    left_xy["sensor"]["frontend_xy"] = frontend_xy
    left_xy["sensor"]["center_xy"] = center_xy
    left_xy["sensor"]["backend_xy"] = backend_xy


# 根据右侧鞋垫所在最小矩形左上角坐标生成左侧鞋垫传感器坐标
def right_map_rule(rectangle_left_top_xy: list, rectangle_width_hight: list, right_xy:dict)->None:
    """
    rectangle_left_top_xy:左上角坐标
    rectangle_width_hight:宽高
    """

    interval = 1
    x1, y1 = rectangle_left_top_xy
    w, h = rectangle_width_hight
    frontend_xy = (x1 + 3 * interval, y1 - 4 * interval)
    # 计算前脚掌坐标
    C1 = frontend_xy
    C2 = (frontend_xy[0] + interval, frontend_xy[1])
    C3 = (frontend_xy[0] + 2 * interval, frontend_xy[1])
    C11 = (C3[0], C3[1] - interval)
    C10 = (C2[0], C2[1] - interval)
    C9 = (C1[0], C1[1] - interval)
    # 前脚掌坐标列表
    frontend_xy = [C1, C2, C3, C9, C10, C11]

    # 计算中脚掌坐标
    C12 = (C11[0], C11[1] - interval)
    C4 = (C12[0] + interval, C12[1])
    C13 = (C11[0], C11[1] - 2 * interval)
    C5 = (C4[0], C4[1] - interval)
    C14 = (C11[0], C11[1] - 3 * interval)
    C6 = (C5[0], C5[1] - interval)
    # 中脚掌坐标
    center_xy = [C12, C4, C13, C5, C14, C6]

    # 计算后脚掌坐标
    C7 = (C14[0], C14[1] - interval)
    C8 = (C14[0], C14[1] - 2 * interval)
    C15 = (C7[0] - interval, C7[1])
    C16 = (C15[0], C15[1] - interval)
    # 后脚掌坐标
    backend_xy = [C7, C15, C8, C16]
    right_xy["sensor"]["frontend_xy"] = frontend_xy
    right_xy["sensor"]["center_xy"] = center_xy
    right_xy["sensor"]["backend_xy"] = backend_xy


def calculate_cop_xy(pressures, coordinates):
    """
    计算压力中心坐标 (X_COP, Y_COP)

    参数:
    pressures: list of float, 各传感器的压力值 F_i
    coordinates: list of tuple, 各传感器的坐标 (x_i, y_i)

    返回:
    (X_COP, Y_COP): tuple of float, 压力中心的坐标
    """
    total_pressure = sum(pressures)

    if total_pressure == 0:
        return (0, 0)  # 防止除以零

    x_cop = sum(F * x for F, (x, _) in zip(pressures, coordinates)) / total_pressure
    y_cop = sum(F * y for F, (_, y) in zip(pressures, coordinates)) / total_pressure

    return (x_cop, y_cop)


def calculate_distances(sensor_coords, center_coords):
    """
    计算每个传感器与压力中心之间的距离。

    参数:
    sensor_coords (ndarray): 传感器坐标数组，形状为 (n, 2)。
    center_coords (tuple): 压力中心的坐标 (x, y)。

    返回:
    ndarray: 每个传感器到压力中心的距离数组。
    """
    sensor_coords = np.array(sensor_coords)
    center_coords = np.array(center_coords)

    # 计算欧氏距离
    distances = np.sqrt(np.sum((sensor_coords - center_coords) ** 2, axis=1))
    return distances


def calculate_F_COP(pressures, distances):
    """
    计算压力中心的等效压力值 (F_COP)

    参数:
    pressures (list or ndarray): 每个传感器的压力值列表或数组。
    distances (list or ndarray): 每个传感器到压力中心的距离列表或数组。

    返回:
    float: 计算得到的 F_COP 值。
    """
    pressures = np.array(pressures)
    distances = np.array(distances)

    numerator = np.sum((pressures**2) / distances)
    denominator = np.sum(pressures / distances)
    F_COP = numerator / denominator
    return F_COP
