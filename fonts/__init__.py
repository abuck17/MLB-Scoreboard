from adafruit_bitmap_font import bitmap_font

basepath = "/fonts/"

small = bitmap_font.load_font(basepath + "bdf/4x6.bdf")
medium = bitmap_font.load_font(basepath + "bdf/5x8.bdf")
large = bitmap_font.load_font(basepath + "bdf/6x10.bdf")