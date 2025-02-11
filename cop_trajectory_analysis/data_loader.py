import pandas as pd
from itertools import chain

class PressureDataLoader:
    """
    压力数据加载器类，用于从CSV文件中加载和处理压力数据。

    属性:
        file_path (str): CSV文件路径。
        sensor_groups (dict): 定义传感器分组的字典。
    """
    def __init__(self, file_path):
        """
        初始化PressureDataLoader类。

        参数:
            file_path (str): CSV文件路径。
        """
        self.file_path = file_path
        self.sensor_groups = {
            "frontend": [
                "sensor1",
                "sensor2",
                "sensor3",
                "sensor9",
                "sensor10",
                "sensor11",
            ],
            "center": [
                "sensor4",
                "sensor5",
                "sensor6",
                "sensor12",
                "sensor13",
                "sensor14",
            ],
            "backend": ["sensor7", "sensor8", "sensor15", "sensor16"],
        }
        self.pressure_data=None

    def load_pressure(self):
        """
        加载CSV文件中的压力数据，并按时间戳分组。

        返回:
            dict: 包含每个时间戳对应的压力数据，按左右脚分组。
        """
        df = pd.read_csv(self.file_path)
        grouped_by_time = df.groupby("timestamp")
        self.pressure_data = {
            timestamp: self._process_group(group)
            for timestamp, group in grouped_by_time
        }
        return self.pressure_data
    def get_total_pressure(self,timestamp_key=None):
        if timestamp_key is None:
            # 处理所有时间戳
            timestamp_keys = self.pressure_data.keys()
        elif isinstance(timestamp_key, str):
            # 处理单个时间戳
            timestamp_keys = [timestamp_key]
        else:
            # 处理多个时间戳
            timestamp_keys = timestamp_key
        total_pressures = {}
        for key in timestamp_keys:
            left_pressures = list(chain.from_iterable(self.pressure_data[key]["left"].values()))
            right_pressures = list(chain.from_iterable(self.pressure_data[key]["right"].values()))
            total_pressure = list(chain.from_iterable([left_pressures, right_pressures]))
            total_pressures[key] = total_pressure
        return total_pressures

    def _process_group(self, group):
        """
        处理每个时间戳的分组数据，分别提取左右脚的数据。

        参数:
            group (DataFrame): 当前时间戳的数据分组。

        返回:
            dict: 包含左右脚分组的压力数据。"0表示left"、"1表示right"）。
        """
        left_data = self._extract_foot_data(group, 0)
        right_data = self._extract_foot_data(group, 1)
        return {"left": left_data, "right": right_data}

    def _extract_foot_data(self, group, foot):
        """
        提取指定脚的压力数据，并按传感器分组。

        参数:
            group (DataFrame): 当前时间戳的数据分组。
            foot (number): 指定提取哪只脚的数据（"0表示left"、"1表示right"）。

        返回:
            dict: 包含按区域分组的压力数据。
        """
        # 假设数据中有一列标识左右脚，例如"foot"
        foot_group = group[group["foot"] == foot]
        pressure_data = {}
        for region, sensors in self.sensor_groups.items():
            pressure_data[region] = foot_group[sensors].values.tolist()[0]
        return pressure_data


class CoordinateDataLoader:
    def __init__(self, file_path,left_map,right_map):
        self.file_path = file_path
        self.rectangle_width_hight= [12, 6] # 鞋垫所在矩形的宽度和高度
        self.left_map_rule: Callable[[list, list, dict], None] = left_map
        self.right_map_rule: Callable[[list, list, dict], None] = right_map
        self.coordinate_groups = {
            "rectangle_left_top_xy": [],  # 鞋垫所在矩形的左上角坐标
            "sensor": {"frontend_xy": [], "center_xy": [], "backend_xy": []},
        }
        self.coordinate_data=None
    def load_coordinates(self):
        # 读取CSV文件并解析坐标数据
        df = pd.read_csv(self.file_path)
        grouped_by_time = df.groupby("timestamp")
        self.coordinate_data ={
            timestamp: self._process_coordinate_group(group)
            for timestamp, group in grouped_by_time
        }
        return self.coordinate_data

    def get_total_coordinate(self, timestamp_key=None):
        if timestamp_key is None:
            # 处理所有时间戳
            timestamp_keys = self.coordinate_data.keys()
        elif isinstance(timestamp_key, str):
            # 处理单个时间戳
            timestamp_keys = [timestamp_key]
        else:
            # 处理多个时间戳
            timestamp_keys = timestamp_key
        total_coordinates = {}
        for key in timestamp_keys:
            left_sensor_xy = self.coordinate_data[key]["left"]["sensor"]
            right_sensor_xy = self.coordinate_data[key]["right"]["sensor"]
            left_xy=chain.from_iterable([left_sensor_xy['frontend_xy'], left_sensor_xy['center_xy'], left_sensor_xy['backend_xy']])
            right_xy=chain.from_iterable([right_sensor_xy['frontend_xy'], right_sensor_xy['center_xy'], right_sensor_xy['backend_xy']])
            total_coordinates[key] = list(chain.from_iterable([left_xy, right_xy]))
        return total_coordinates

    def _process_coordinate_group(self, group):
        """
        处理每个时间戳的分组数据，分别提取左右脚的数据。

        参数:
            group (DataFrame): 当前时间戳的数据分组。

        返回:
            dict: 包含左右脚分组的压力数据。
        """
        left_data = self._extract_coordinate_data(group, 0)
        right_data = self._extract_coordinate_data(group, 1)
        return {"left": left_data, "right": right_data}

    def _extract_coordinate_data(self, group, foot):
        """
        提取指定脚的压力数据，并按传感器分组。

        参数:
            group (DataFrame): 当前时间戳的数据分组。
            foot (number): 指定提取哪只脚的数据（"0表示left"、"1表示right"）。

        返回:
            dict: 包含按区域分组的压力数据。
        """
        # 假设数据中有一列标识左右脚，例如"foot"
        foot_group = group[group["foot"] == foot]
        coordinate_data = {key: value.copy() if isinstance(value, dict) else value for key, value in self.coordinate_groups.items()}
        coordinate_data["rectangle_left_top_xy"] = foot_group[
            ["x", "y"]
        ].values.tolist()[0]
        # 使用字典映射来选择映射规则
        map_rules = {
            0: self.left_map_rule,
            1: self.right_map_rule
        }

        map_rules[foot](coordinate_data["rectangle_left_top_xy"], self.rectangle_width_hight, coordinate_data)
        return coordinate_data
