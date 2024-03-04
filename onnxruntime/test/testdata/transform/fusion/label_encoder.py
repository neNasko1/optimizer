from enum import Enum  # noqa: F401

import onnx
from onnx import OperatorSetIdProto, TensorProto, helper

opsets = []
onnxdomain = OperatorSetIdProto()
onnxdomain.version = 19
onnxdomain.domain = ""  # The empty string ("") or absence of this field implies the operator set that is defined as part of the ONNX specification.
opsets.append(onnxdomain)

msdomain = OperatorSetIdProto()
msdomain.version = 1
msdomain.domain = "com.microsoft"
opsets.append(msdomain)

ai_ml_domain = OperatorSetIdProto()
ai_ml_domain.version = 4
ai_ml_domain.domain = "ai.onnx.ml"
opsets.append(ai_ml_domain)

kwargs = {}
kwargs["opset_imports"] = opsets


def GenerateModel(model_name):  # noqa: N802
    # Create models with consecutive label encoders
    nodes = [  # subgraph
        # string -> int -> string
        helper.make_node(
            "LabelEncoder",
            ["A"], 
            ["le_1_int_1"], 
            "le_1_int_1",
            domain="ai.onnx.ml",
            keys_strings=["a", "b", "c"],
            values_int64s=[0, 1, 2],
        ),
        helper.make_node(
            "LabelEncoder", 
            ["le_1_int_1"], 
            ["le_1_string_2"], 
            "le_1_string_2",
            domain="ai.onnx.ml",
            keys_int64s=[2, 1, 0],
            values_strings=["a", "b", "c"],
            default_string="default"
        ),
        # middle encoder is consumed twice
        helper.make_node(
            "LabelEncoder",
            ["A"], 
            ["le_2_int_1"], 
            "le_2_int_1",
            domain="ai.onnx.ml",
            keys_strings=["a", "b", "c"],
            values_int64s=[0, 1, 2],
        ),
        helper.make_node(
            "LabelEncoder", 
            ["le_2_int_1"], 
            ["le_2_string_2"], 
            "le_2_string_2",
            domain="ai.onnx.ml",
            keys_int64s=[0, 1, 2],
            values_strings=["a", "b", "c"],
        ),
        helper.make_node("Mul", ["le_2_int_1", "le_2_int_1"], ["mul_2"], "mul_2"),
        # middle encoder is graph output
        helper.make_node(
            "LabelEncoder",
            ["A"], 
            ["le_3_int_1"], 
            "le_3_int_1",
            domain="ai.onnx.ml",
            keys_strings=["a", "b", "c"],
            values_int64s=[0, 1, 2],
        ),
        helper.make_node(
            "LabelEncoder", 
            ["le_3_int_1"], 
            ["le_3_string_2"], 
            "le_3_string_2",
            domain="ai.onnx.ml",
            keys_int64s=[0, 1, 2],
            values_strings=["a", "b", "c"],
        ),
        helper.make_node("Identity", ["le_3_int_1"], ["Y"], "output"),
    ]

    inputs = [  # inputs
        helper.make_tensor_value_info("A", TensorProto.STRING, ["M", "K"]),
    ]

    graph = helper.make_graph(
        nodes,
        "LabelEncoder",  # name
        inputs,
        [  # outputs
            helper.make_tensor_value_info("le_1_string_2", TensorProto.STRING, ["M", "K"]),
            helper.make_tensor_value_info("le_3_string_2", TensorProto.STRING, ["M", "K"]),
            helper.make_tensor_value_info("le_3_string_2", TensorProto.STRING, ["M", "K"]),
            helper.make_tensor_value_info("Y", TensorProto.INT64, ["M", "K"]),
        ],
        [],
    )

    model = helper.make_model(graph, **kwargs)
    onnx.save(model, model_name)


if __name__ == "__main__":
    GenerateModel("label_encoder.onnx")
