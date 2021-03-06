import torch
import torch.nn as nn
from models.layers import RegularBlock, Features_2_to_1


class BaseModel(nn.Module):
    def __init__(self, original_features_num, num_blocks, in_features,out_features, depth_of_mlp):
        """
        take a batch of graphs (bs, n_vertices, n_vertices, in_features)
        and return a batch of graphs with new features
        graphs must have same size inside the batch
        """
        super().__init__()

        self.original_features_num = original_features_num
        self.num_blocks = num_blocks
        self.in_features = in_features
        self.out_features = out_features
        self.depth_of_mlp =depth_of_mlp
        
        # First part - sequential mlp blocks
        last_layer_features = self.original_features_num
        self.reg_blocks = nn.ModuleList()
        for _ in range(self.num_blocks-1):
            mlp_block = RegularBlock(last_layer_features, in_features, self.depth_of_mlp)
            self.reg_blocks.append(mlp_block)
            last_layer_features = in_features
        mlp_block = RegularBlock(in_features,out_features,depth_of_mlp)
        self.reg_blocks.append(mlp_block)

    def forward(self, x):
        #here x.shape = (bs, n_vertices, n_vertices, n_features)
        if x.shape[3] != self.original_features_num:
            print("expected input feature {} and got {}".format(self.original_features_num,x.shape[3]))
            return
        x = x.permute(0, 3, 1, 2)
        #expects x.shape = (bs, n_features, n_vertices, n_vertices)
        for block in self.reg_blocks:
            x = block(x)
        # return (bs, n_vertices, n_vertices, n_features)
        return x.permute(0,2,3,1)

class Simple_Node_Embedding(nn.Module):
    def __init__(self, original_features_num, num_blocks, in_features,out_features, depth_of_mlp):
        """
        take a batch of graphs (bs, n_vertices, n_vertices, in_features)
        and return a batch of node embedding (bs, n_vertices, out_features)
        graphs must have same size inside the batch
        """
        super().__init__()

        self.original_features_num = original_features_num
        self.num_blocks = num_blocks
        self.in_features = in_features
        self.out_features = out_features
        self.depth_of_mlp =depth_of_mlp
        self.base_model = BaseModel(original_features_num, num_blocks, in_features,out_features, depth_of_mlp)
        self.suffix = Features_2_to_1()

    def forward(self, x):
        x = self.base_model(x)
        x = self.suffix(x)
        return  x
