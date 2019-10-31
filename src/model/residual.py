from keras.layers import BatchNormalization, Conv2D, add
from keras.layers import LeakyReLU
from keras.regularizers import l2
import config

def conv_block(feat_maps_out, prev):
    prev = Conv2D(feat_maps_out, kernel_size=config.KERNEL_SIZE, strides=1, padding="same",
                  use_bias=config.USE_BIAS, kernel_regularizer=l2(config.REGULARIZER_CONST))(prev)
    prev = BatchNormalization()(prev)
    prev = LeakyReLU()(prev)
    prev = Conv2D(feat_maps_out, kernel_size=config.KERNEL_SIZE, strides=1, padding="same",
                  use_bias=config.USE_BIAS, kernel_regularizer=l2(config.REGULARIZER_CONST))(prev)
    prev = BatchNormalization()(prev)
    return prev

def skip_block(feat_maps_in, feat_maps_out, prev):
    if feat_maps_in != feat_maps_out:
        # This adds in a 1x1 convolution on shortcuts that map between an uneven amount of channels
        prev = Conv2D(feat_maps_out, kernel_size=1, strides=1, padding="same",
                      use_bias=config.USE_BIAS, kernel_regularizer=l2(config.REGULARIZER_CONST))(prev)
    return prev

def Residual(feat_maps_in, feat_maps_out, prev_layer):
    """
    A customizable residual unit with convolutional and shortcut blocks
    Args:
      feat_maps_in: number of channels/filters coming in, from input or previous layer
      feat_maps_out: how many output channels/filters this block will produce
      prev_layer: the previous layer
    """
    skip = skip_block(feat_maps_in, feat_maps_out, prev_layer)
    conv = conv_block(feat_maps_out, prev_layer)

    merged = add([skip, conv]) # the residual connection

    return LeakyReLU()(merged)
