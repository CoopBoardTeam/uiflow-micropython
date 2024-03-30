// Include MicroPython API.
#include "py/runtime.h"
#include "config.h"
#include "managed_i2c.h"
#include "pca9555.h"
// Espressif IDF requires "freertos/" prefix in include path
#define CFG_TUSB_OS_INC_PATH  freertos/
#include "tinyusb.h"
#include "class/hid/hid_device.h"


static PCA9555 colport;
static PCA9555 rowport;


// This is the function which will be called from Python as cexample.add_ints(a, b).
static mp_obj_t coopboard_add_ints(mp_obj_t a_obj, mp_obj_t b_obj) {
    // Extract the ints from the micropython input objects.
    mp_obj_t ret_list = mp_obj_new_list(0, NULL);
    int a = mp_obj_get_int(a_obj);
    int b = mp_obj_get_int(b_obj);
    mp_obj_list_append(ret_list, mp_obj_new_int_from_uint(a + b));


    // Calculate the addition and convert to MicroPython object.
    return ret_list;
}
// Define a Python reference to the function above.
static MP_DEFINE_CONST_FUN_OBJ_2(coopboard_add_ints_obj, coopboard_add_ints);


//////////////////////////// pca 9555 ////////////////////////////////////
static mp_obj_t coopboard_board_scan_init() {
    i2c_init(0, SYS_SDA_PIN, SYS_SCL_PIN, 400000, true, true);
    pca9555_init(&colport, 0, COL_9555_ADDR, INTERRUPT_PIN);
    pca9555_init(&rowport, 0, ROW_9555_ADDR, INTERRUPT_PIN);
    for (uint8_t i = 0; i < 4; i++){  //行设为输出
        pca9555_set_gpio_direction(&rowport, i, PCA9555_DIR_OUT);
        pca9555_set_gpio_value(&rowport, i, 1);
    }
    for (uint8_t i = 0; i < 16; i++){  //列设为输入
        pca9555_set_gpio_direction(&colport, i, PCA9555_DIR_IN);
    }
    return mp_const_true;
}
static MP_DEFINE_CONST_FUN_OBJ_0(coopboard_board_scan_init_obj, coopboard_board_scan_init);


static mp_obj_t coopboard_board_scan() {
    mp_obj_t ret_list = mp_obj_new_list(0, NULL);
    const uint8_t row_num = 4;
    const uint8_t col_num = 16;
    for (uint8_t i = 0; i < row_num; i++){
        pca9555_set_gpio_value(&rowport, (i + 3) % row_num, 1);
        pca9555_set_gpio_value(&rowport, i, 0);
        for (uint8_t j = 0; j < col_num; j++){
            bool ret;
            pca9555_get_gpio_value(&colport, j, &ret);
            if (!ret) {
                mp_obj_t rc_tuple = mp_obj_new_list(0, NULL);
                mp_obj_list_append(rc_tuple, mp_obj_new_int_from_uint(i));
                mp_obj_list_append(rc_tuple, mp_obj_new_int_from_uint(j));
                mp_obj_list_append(ret_list, rc_tuple);
            }
        }
    }
    return ret_list;
}
static MP_DEFINE_CONST_FUN_OBJ_0(coopboard_board_scan_obj, coopboard_board_scan);


//////////////////////////// pca 9555 END ////////////////////////////////
//////////////////////////// hid control port ////////////////////////////////
static mp_obj_t coopboard_sendkey(size_t n_args, const mp_obj_t *args) {
    // Extract the ints from the micropython input objects.
    uint8_t kbid = mp_obj_get_int(args[0]);
    uint8_t composite_code = mp_obj_get_int(args[1]);
    uint8_t codes[6] = {0};
    for (size_t i = 0; i < n_args-2; i++) {
        codes[i] = mp_obj_get_int(args[i+2]);
    }
    // keyboard id, report id, modifier, keycode[6]
    tud_hid_n_keyboard_report(0, HID_ITF_PROTOCOL_KEYBOARD, composite_code, codes);
    return mp_const_true;
}
// Define a Python reference to the function above.
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(coopboard_sendkey_obj, 2, 8, coopboard_sendkey);

static mp_obj_t coopboard_sendmouse(size_t n_args, const mp_obj_t *args) {
    // Extract the ints from the micropython input objects.
    uint8_t mouseid_c = mp_obj_get_int(args[0]);
    uint8_t buttons_c = mp_obj_get_int(args[1]);
    uint8_t dx_c = mp_obj_get_int(args[2]);
    uint8_t dy_c = mp_obj_get_int(args[3]);
    uint8_t vertical_c = mp_obj_get_int(args[4]);
    uint8_t horizonta_c = mp_obj_get_int(args[5]);
    // n_mouse_id, uint8_t report_id, uint8_t buttons, int8_t x, int8_t y, int8_t vertical, int8_t horizontal
    tud_hid_n_mouse_report(mouseid_c, HID_ITF_PROTOCOL_MOUSE, buttons_c, dx_c, dy_c, vertical_c, horizonta_c);
    // Calculate the addition and convert to MicroPython object.
    return mp_const_true;
}
// Define a Python reference to the function above.
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(coopboard_sendmouse_obj, 6, 6, coopboard_sendmouse);



//////////////////////////// hid control port END ////////////////////////////////

// Define all attributes of the module.
// Table entries are key/value pairs of the attribute name (a string)
// and the MicroPython object reference.
// All identifiers and strings are written as MP_QSTR_xxx and will be
// optimized to word-sized integers by the build system (interned strings).
static const mp_rom_map_elem_t coopboard_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_coopboard) },
    { MP_ROM_QSTR(MP_QSTR_add_ints), MP_ROM_PTR(&coopboard_add_ints_obj) },
    { MP_ROM_QSTR(MP_QSTR_board_scan_init), MP_ROM_PTR(&coopboard_board_scan_init_obj) },
    { MP_ROM_QSTR(MP_QSTR_board_scan), MP_ROM_PTR(&coopboard_board_scan_obj) },
    { MP_ROM_QSTR(MP_QSTR_sendkey), MP_ROM_PTR(&coopboard_sendkey_obj) },
    { MP_ROM_QSTR(MP_QSTR_sendmouse), MP_ROM_PTR(&coopboard_sendmouse_obj) },
};
static MP_DEFINE_CONST_DICT(coopboard_module_globals, coopboard_module_globals_table);

// Define module object.
const mp_obj_module_t coopboard_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&coopboard_module_globals,
};

// Register the module to make it available in Python.
MP_REGISTER_MODULE(MP_QSTR_coopboard, coopboard_user_cmodule);


