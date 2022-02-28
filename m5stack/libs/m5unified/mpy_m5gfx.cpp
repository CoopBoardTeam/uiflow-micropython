#include <M5GFX.h>

#include <ffi.h>
typedef union {
  ffi_sarg sint;
  ffi_arg  uint;
  float    flt;
  double   dbl;
  void*    ptr;
} ffi_value;

extern "C"
{
  #include <extmod/vfs.h>
  #include <extmod/vfs_lfs.h>
  #include <lib/littlefs/lfs2.h>
  #include <py/obj.h>
  #include "mpy_m5gfx.h"
  #include "esp_log.h"

  typedef struct _mp_obj_vfs_lfs2_t {
    mp_obj_base_t base;
    mp_vfs_blockdev_t blockdev;
    bool enable_mtime;
    vstr_t cur_dir;
    struct lfs2_config config;
    lfs2_t lfs;
  } mp_obj_vfs_lfs2_t;

  struct LFS2Wrapper : public m5gfx::DataWrapper
  {
    LFS2Wrapper() : DataWrapper()
    {
      need_transaction = true;
    }

    // Not formatted yet, only for micropython porting
    bool open(const char* path) override {
      const char* full_path;
      struct lfs2_info _finfo;
      mp_vfs_mount_t* _fm = mp_vfs_lookup_path(path, &full_path);
      if (_fm == MP_VFS_NONE || _fm == MP_VFS_ROOT) {
        if (_fm == MP_VFS_NONE) mp_printf(&mp_plat_print, "path not found");
        if (_fm == MP_VFS_ROOT)
            mp_printf(&mp_plat_print, "path is \"\" or \"/\"");
        return false;
      }
      _fp = &((mp_obj_vfs_lfs2_t*)MP_OBJ_TO_PTR(_fm->obj))->lfs;
      enum lfs2_error res = (lfs2_error)lfs2_stat(_fp, full_path, &_finfo);
      if (res != LFS2_ERR_OK) {
        mp_printf(&mp_plat_print, "%s\r\n", strerror(res));
        return false;
      }
      _file = (lfs2_file_t*)malloc(1 * sizeof(lfs2_file_t));
      memset(&_fcfg, 0, sizeof(lfs2_file_config));
      _fcfg.buffer = malloc(_fp->cfg->cache_size * sizeof(uint8_t));
      return ((lfs2_file_opencfg(_fp, _file, full_path,
                                LFS2_O_RDWR | LFS2_O_CREAT,
                                &_fcfg) == LFS2_ERR_OK)
                ? true
                : false);
    }
    int read(uint8_t* buf, uint32_t len) override {
      return lfs2_file_read(_fp, _file, (char*)buf, len);
    }
    void skip(int32_t offset) override {
      lfs2_file_seek(_fp, _file, offset, LFS2_SEEK_CUR);
    }
    bool seek(uint32_t offset) override {
      return lfs2_file_seek(_fp, _file, offset, LFS2_SEEK_SET);
    }
    bool seek(uint32_t offset, int origin) {
      return lfs2_file_seek(_fp, _file, offset, origin);
    }
    void close() override {
      if (_fp) lfs2_file_close(_fp, _file);
      if (_file) free(_file);
      if (_fcfg.buffer) free(_fcfg.buffer);
    }
    int32_t tell(void) override {
      return lfs2_file_tell(_fp, _file);
    }

   protected:
    lfs2_t* _fp        = nullptr;
    lfs2_file_t* _file = nullptr;
    struct lfs2_file_config _fcfg;
  };

  static inline LovyanGFX* getGfx(const mp_obj_t* args)
  {
    return (LovyanGFX*)(((gfx_obj_t*)MP_OBJ_TO_PTR(args[0]))->gfx);
  }

//-------- GFX common wrapper

  mp_obj_t gfx_width(mp_obj_t self)
  {
    auto gfx = getGfx(&self);
    return mp_obj_new_int(gfx->width());
  }

  mp_obj_t gfx_height(mp_obj_t self)
  {
    auto gfx = getGfx(&self);
    return mp_obj_new_int(gfx->height());
  }

  mp_obj_t gfx_getRotation(mp_obj_t self)
  {
    auto gfx = getGfx(&self);
    return mp_obj_new_int(gfx->getRotation());
  }

  mp_obj_t gfx_getColorDepth(mp_obj_t self)
  {
    auto gfx = getGfx(&self);
    return mp_obj_new_int(gfx->getColorDepth());
  }

  mp_obj_t gfx_setRotation(mp_obj_t self, mp_obj_t r)
  {
    auto gfx = getGfx(&self);
    gfx->setRotation(mp_obj_get_int(r));
    return mp_const_none;
  }

  mp_obj_t gfx_setColorDepth(mp_obj_t self, mp_obj_t bpp)
  {
    auto gfx = getGfx(&self);
    gfx->setColorDepth(mp_obj_get_int(bpp));
    return mp_const_none;
  }

  mp_obj_t gfx_print(size_t n_args, const mp_obj_t *args)
  {
    auto gfx = getGfx(args);
    if (n_args >= 3) { gfx->setTextColor((uint32_t)mp_obj_get_int(args[2])); }
    gfx->print( mp_obj_str_get_str(args[1]));
    return mp_const_none;
  }

  mp_obj_t gfx_setCursor(mp_obj_t self, mp_obj_t x, mp_obj_t y)
  {
    auto gfx = getGfx(&self);
    gfx->setCursor( mp_obj_get_int(x)
                  , mp_obj_get_int(y)
                  );
    return mp_const_none;
  }

  mp_obj_t gfx_getCursor(mp_obj_t self)
  {
    auto gfx = getGfx(&self);
    mp_obj_t tuple[2] = { mp_obj_new_int(gfx->getCursorX())
                        , mp_obj_new_int(gfx->getCursorY())
                        };
    return mp_obj_new_tuple(2, tuple);
  }

  mp_obj_t gfx_setFont(mp_obj_t self, mp_obj_t font)
  {
    auto gfx = getGfx(&self);
    gfx->setFont((const m5gfx::IFont*) ((font_obj_t*)MP_OBJ_TO_PTR(font))->font);
    return mp_const_none;
  }

  mp_obj_t gfx_setTextColor(mp_obj_t self, mp_obj_t color)
  {
    auto gfx = getGfx(&self);
    gfx->setTextColor((uint32_t)mp_obj_get_int(color));
    return mp_const_none;
  }

  mp_obj_t gfx_setTextScroll(mp_obj_t self, mp_obj_t scroll)
  {
    auto gfx = getGfx(&self);
    gfx->setTextScroll((bool)mp_obj_get_int(scroll));
    return mp_const_none;
  }

  mp_obj_t gfx_clear(size_t n_args, const mp_obj_t *args)
  {
    auto gfx = getGfx(args);
    if (n_args >= 2) { gfx->setBaseColor((uint32_t)mp_obj_get_int(args[1])); }
    gfx->clear();
    return mp_const_none;
  }

  mp_obj_t gfx_fillScreen(size_t n_args, const mp_obj_t *args)
  {
    auto gfx = getGfx(args);
    if (n_args >= 2) { gfx->setColor((uint32_t)mp_obj_get_int(args[1])); }
    gfx->fillScreen();
    return mp_const_none;
  }

  mp_obj_t gfx_drawPixel(size_t n_args, const mp_obj_t *args)
  {
    auto gfx = getGfx(args);
    if (n_args >= 4) { gfx->setColor((uint32_t)mp_obj_get_int(args[3])); }
    gfx->drawPixel( mp_obj_get_int(args[1])
                  , mp_obj_get_int(args[2])
                  );
    return mp_const_none;
  }

  mp_obj_t gfx_drawCircle(size_t n_args, const mp_obj_t *args)
  {
    auto gfx = getGfx(args);
    if (n_args >= 5) { gfx->setColor((uint32_t)mp_obj_get_int(args[4])); }
    gfx->drawCircle( mp_obj_get_int(args[1])
                   , mp_obj_get_int(args[2])
                   , mp_obj_get_int(args[3])
                   );
    return mp_const_none;
  }

  mp_obj_t gfx_fillCircle(size_t n_args, const mp_obj_t *args)
  {
    auto gfx = getGfx(args);
    if (n_args >= 5) { gfx->setColor((uint32_t)mp_obj_get_int(args[4])); }
    gfx->fillCircle( mp_obj_get_int(args[1])
                   , mp_obj_get_int(args[2])
                   , mp_obj_get_int(args[3])
                   );
    return mp_const_none;
  }

  mp_obj_t gfx_drawLine(size_t n_args, const mp_obj_t *args)
  {
    auto gfx = getGfx(args);
    if (n_args >= 6) { gfx->setColor((uint32_t)mp_obj_get_int(args[5])); }
    gfx->drawLine( mp_obj_get_int(args[1])
                 , mp_obj_get_int(args[2])
                 , mp_obj_get_int(args[3])
                 , mp_obj_get_int(args[4])
                 );
    return mp_const_none;
  }

  mp_obj_t gfx_drawRect(size_t n_args, const mp_obj_t *args)
  {
    auto gfx = getGfx(args);
    if (n_args >= 6) { gfx->setColor((uint32_t)mp_obj_get_int(args[5])); }
    gfx->drawRect( mp_obj_get_int(args[1])
                 , mp_obj_get_int(args[2])
                 , mp_obj_get_int(args[3])
                 , mp_obj_get_int(args[4])
                 );
    return mp_const_none;
  }

  mp_obj_t gfx_fillRect(size_t n_args, const mp_obj_t *args)
  {
    auto gfx = getGfx(args);
    if (n_args >= 6) { gfx->setColor((uint32_t)mp_obj_get_int(args[5])); }
    gfx->fillRect( mp_obj_get_int(args[1])
                 , mp_obj_get_int(args[2])
                 , mp_obj_get_int(args[3])
                 , mp_obj_get_int(args[4])
                 );
    return mp_const_none;
  }

  mp_obj_t gfx_drawRoundRect(size_t n_args, const mp_obj_t *args)
  {
    auto gfx = getGfx(args);
    if (n_args >= 7) { gfx->setColor((uint32_t)mp_obj_get_int(args[6])); }
    gfx->drawRoundRect( mp_obj_get_int(args[1])
                      , mp_obj_get_int(args[2])
                      , mp_obj_get_int(args[3])
                      , mp_obj_get_int(args[4])
                      , mp_obj_get_int(args[5])
                      );
    return mp_const_none;
  }

  mp_obj_t gfx_fillRoundRect(size_t n_args, const mp_obj_t *args)
  {
    auto gfx = getGfx(args);
    if (n_args >= 7) { gfx->setColor((uint32_t)mp_obj_get_int(args[6])); }
    gfx->fillRoundRect( mp_obj_get_int(args[1])
                      , mp_obj_get_int(args[2])
                      , mp_obj_get_int(args[3])
                      , mp_obj_get_int(args[4])
                      , mp_obj_get_int(args[5])
                      );
    return mp_const_none;
  }

  mp_obj_t gfx_printf(size_t n_args, const mp_obj_t *args)
  {
    auto types  = (ffi_type**)alloca(n_args * sizeof(ffi_type *));
    auto values = (ffi_value*)alloca(n_args * sizeof(ffi_value));
    auto arg_values = (void**)alloca(n_args * sizeof(void *));

    size_t i;
    types[0] = &ffi_type_pointer;
    values[0].ptr = getGfx(args);
    arg_values[0] = &values[0];
    for (i = 1; i < n_args; i++) {
      if (mp_obj_get_int_maybe(args[i], (mp_int_t *)&values[i].sint)) {
        types[i] = &ffi_type_sint;
      } else if (mp_obj_is_float(args[i])) {
        types[i] = &ffi_type_double;
        values[i].dbl = mp_obj_get_float_to_d(args[i]);
      } else if (mp_obj_is_str(args[i])) {
        types[i] = &ffi_type_pointer;
        values[i].ptr = (void *)mp_obj_str_get_str(args[i]);
      } else {
        // ERROR
        mp_raise_TypeError(MP_ERROR_TEXT("not supported type is specified"));
      }
      arg_values[i] = &values[i];
    }

    ffi_cif cif;
    ffi_prep_cif_var(&cif, FFI_DEFAULT_ABI, 1, n_args, &ffi_type_sint, types);
    ffi_arg result;
    ffi_call(&cif, FFI_FN(&LovyanGFX::printf), &result, arg_values);

    return mp_const_none;
  }

  mp_obj_t gfx_drawBmp(size_t n_args, const mp_obj_t *args)
  {
    auto gfx = getGfx(args);
    if (mp_obj_is_str(args[1]) && ((size_t)mp_obj_len(args[1]) < 128)) // file
    {
      LFS2Wrapper wrapper;
      gfx->drawBmpFile( &wrapper
                      , mp_obj_str_get_str(args[1])
                      , mp_obj_get_int(args[2])
                      , mp_obj_get_int(args[3])
                      , 0, 0, 0, 0, 1.0f, 0.0f, m5gfx::datum_t::top_left);
    }
    else // buffer
    {
      mp_buffer_info_t bufinfo;
      mp_get_buffer_raise(args[1], &bufinfo, MP_BUFFER_READ);
      gfx->drawBmp( (const uint8_t*)bufinfo.buf
                  , bufinfo.len
                  , mp_obj_get_int(args[2])
                  , mp_obj_get_int(args[3]));
    }
    return mp_const_none;
  }

  mp_obj_t gfx_drawJpg(size_t n_args, const mp_obj_t *args)
  {
    auto gfx = getGfx(args);
    if (mp_obj_is_str(args[1]) && ((size_t)mp_obj_len(args[1]) < 128)) // file
    {
      LFS2Wrapper wrapper;
      gfx->drawJpgFile( &wrapper
                      , mp_obj_str_get_str(args[1])
                      , mp_obj_get_int(args[2])
                      , mp_obj_get_int(args[3]));
    }
    else // buffer
    {
      mp_buffer_info_t bufinfo;
      mp_get_buffer_raise(args[1], &bufinfo, MP_BUFFER_READ);
      gfx->drawJpg( (const uint8_t*)bufinfo.buf
                  , bufinfo.len
                  , mp_obj_get_int(args[2])
                  , mp_obj_get_int(args[3]));
    }
    return mp_const_none;
  }

  mp_obj_t gfx_drawPng(size_t n_args, const mp_obj_t *args)
  {
    auto gfx = getGfx(args);
    if (mp_obj_is_str(args[1]) && ((size_t)mp_obj_len(args[1]) < 128)) // file
    {
      LFS2Wrapper wrapper;
      gfx->drawPngFile( &wrapper
                      , mp_obj_str_get_str(args[1])
                      , mp_obj_get_int(args[2])
                      , mp_obj_get_int(args[3]));
    }
    else // buffer
    {
      mp_buffer_info_t bufinfo;
      mp_get_buffer_raise(args[1], &bufinfo, MP_BUFFER_READ);
      gfx->drawPng( (const uint8_t*)bufinfo.buf
                  , bufinfo.len
                  , mp_obj_get_int(args[2])
                  , mp_obj_get_int(args[3]));
    }
    return mp_const_none;
  }

  mp_obj_t gfx_drawImage(size_t n_args, const mp_obj_t *args)
  {
    auto gfx = getGfx(args);
    if (mp_obj_is_str(args[1]) && ((size_t)mp_obj_len(args[1]) < 128)) // file
    {
      char ftype[5] = {0};
      const char *file_path = mp_obj_str_get_str(args[1]);

      for (size_t i = 0; i < 4; i++)
      {
        ftype[i] = tolower((char)file_path[i + strlen(file_path) - 4]);
      }
      ftype[4] = '\0';

      LFS2Wrapper wrapper;
      if (strstr(ftype, "bmp") != NULL)
      {
        gfx->drawBmpFile( &wrapper
                        , file_path
                        , mp_obj_get_int(args[2])
                        , mp_obj_get_int(args[3]));
      }
      else if ((strstr(ftype, "jpg") != NULL) || (strstr(ftype, "jpeg") != NULL))
      {
        gfx->drawJpgFile( &wrapper
                        , file_path
                        , mp_obj_get_int(args[2])
                        , mp_obj_get_int(args[3]));
      }
      else if (strstr(ftype, "png") != NULL)
      {
        gfx->drawPngFile( &wrapper
                        , file_path
                        , mp_obj_get_int(args[2])
                        , mp_obj_get_int(args[3]));
      }
    }
    else // buffer
    {
      mp_buffer_info_t bufinfo;
      mp_get_buffer_raise(args[1], &bufinfo, MP_BUFFER_READ);
      uint8_t* type_ptr = (uint8_t *)bufinfo.buf;

      if ((type_ptr[0] == 0x42) && (type_ptr[1] == 0x4D))
      {
        gfx->drawBmp( (const uint8_t*)bufinfo.buf
                    , bufinfo.len
                    , mp_obj_get_int(args[2])
                    , mp_obj_get_int(args[3]));
      }
      else if ((type_ptr[0] == 0xFF) && (type_ptr[1] == 0xD8))
      {
        gfx->drawJpg( (const uint8_t*)bufinfo.buf
                    , bufinfo.len
                    , mp_obj_get_int(args[2])
                    , mp_obj_get_int(args[3]));
      }
      else if ((type_ptr[0] == 0x89) && (type_ptr[1] == 0x50))
      {
        gfx->drawPng( (const uint8_t*)bufinfo.buf
                    , bufinfo.len
                    , mp_obj_get_int(args[2])
                    , mp_obj_get_int(args[3]));
      }
    }
    return mp_const_none;
  }

  mp_obj_t gfx_drawQR(size_t n_args, const mp_obj_t *args)
  {
    auto gfx = getGfx(args);
    gfx->qrcode( mp_obj_str_get_str(args[1])
               , mp_obj_get_int(args[2])
               , mp_obj_get_int(args[3])
               , mp_obj_get_int(args[4])
               , mp_obj_get_int(args[5]));
    return mp_const_none;
  }

  mp_obj_t gfx_newCanvas(size_t n_args, const mp_obj_t *args)
  {
    auto gfx = getGfx(args);
    auto canvas = new M5Canvas(gfx);
    if (n_args >= 5) { canvas->setPsram(mp_obj_get_int(args[4])); }
    if (n_args >= 4) { canvas->setColorDepth(mp_obj_get_int(args[3])); }
    if (n_args >= 3) { canvas->createSprite(mp_obj_get_int(args[1]), mp_obj_get_int(args[2])); }
    gfx_obj_t *res = m_new_obj_with_finaliser(gfx_obj_t);
    res->base.type = &gfxcanvas_type;
    res->gfx = canvas;
    return MP_OBJ_FROM_PTR(res);
  }

//-------- GFX device wrapper

  mp_obj_t gfx_startWrite(mp_obj_t self)
  {
    auto gfx = getGfx(&self);
    gfx->startWrite();
    return mp_const_none;
  }

  mp_obj_t gfx_endWrite(mp_obj_t self)
  {
    auto gfx = getGfx(&self);
    gfx->endWrite();
    return mp_const_none;
  }

//-------- GFX canvas wrapper

  mp_obj_t gfx_push(mp_obj_t self, mp_obj_t x, mp_obj_t y)
  {
    auto gfx = getGfx(&self);
    if (gfx)
    {
      ((M5Canvas*)gfx)->pushSprite(mp_obj_get_int(x), mp_obj_get_int(y));
    }
    return mp_const_none;
  }

  mp_obj_t gfx_delete(mp_obj_t self)
  {
    auto gfx = getGfx(&self);
    if (gfx)
    {
      ((M5Canvas*)gfx)->deleteSprite();
      delete (M5Canvas*)gfx;
      ((gfx_obj_t*)MP_OBJ_TO_PTR(self))->gfx = nullptr;
    }
    return mp_const_none;
  }

// stream functions
  mp_uint_t gfx_read(mp_obj_t self, void *buf, mp_uint_t size, int *errcode)
  {
    return 0;
  }

  mp_uint_t gfx_write(mp_obj_t self, const byte *buf, mp_uint_t size, int *errcode)
  {
    auto gfx = getGfx(&self);

    static int32_t last_y_offset = gfx->getCursorY();
    const byte *i = buf;
    gfx->fillRect(gfx->getCursorX(), gfx->getCursorY(), gfx->fontWidth(), gfx->fontHeight(), gfx->getTextStyle().back_rgb888);
    while (i < buf + size)
    {
      uint8_t c = (uint8_t)utf8_get_char(i);
      i = utf8_next_char(i);
      if (c < 128)
      {
        if (c >= 0x20 && c <= 0x7e)
        {
          gfx->write(c);
        }
        else if (c == '\r')
        {
          gfx->write(c);
        }
        else if (c == '\n')
        {
          gfx->write(c);
          last_y_offset = gfx->getCursorY();
        }
        // Commands below are used by MicroPython in the REPL
        else if (c == '\b')
        {
          int16_t x_offset = gfx->getCursorX();
          int16_t y_offset = gfx->getCursorY();
          if (x_offset == 0) {
            x_offset = (int16_t)(gfx->fontWidth() * (gfx->width() / gfx->fontWidth()));
            y_offset = y_offset - gfx->fontHeight();
          }
          gfx->setCursor(x_offset - gfx->fontWidth(), y_offset);
        }
        else if (c == 0x1b)
        {
          if (i[0] == '[')
          {
            if (i[1] == 'K')
            {
              gfx->fillRect(gfx->getCursorX(), gfx->getCursorY(), gfx->fontWidth(), gfx->fontHeight(), gfx->getTextStyle().back_rgb888);
              i += 2;
            }
            else {
              // Handle commands of the form \x1b[####D
              uint16_t n = 0;
              uint8_t j = 1;
              for (; j < 6; j++)
              {
                if ('0' <= i[j] && i[j] <= '9')
                {
                  n = n * 10 + (i[j] - '0');
                }
                else
                {
                  c = i[j];
                  break;
                }
              }
              if (c == 'D')
              {
                // UP and DOWN KEY
                if (gfx->getCursorY() > last_y_offset)
                {
                  do {
                    gfx->fillRect(0, gfx->getCursorY(), gfx->width(), gfx->fontHeight(), gfx->getTextStyle().back_rgb888);
                    gfx->setCursor(gfx->getCursorX(), (gfx->getCursorY() - gfx->fontHeight()));
                  } while (gfx->getCursorY() > last_y_offset);
                  gfx->setCursor((gfx->fontWidth() * (gfx->width() / gfx->fontWidth())), last_y_offset);
                }
                if (gfx->getCursorY() == last_y_offset)
                {
                  gfx->fillRect((gfx->fontWidth() * 4), gfx->getCursorY(), (gfx->width() - gfx->fontWidth() * 4), gfx->fontHeight(), gfx->getTextStyle().back_rgb888);
                  gfx->setCursor((gfx->fontWidth() * 4), gfx->getCursorY());
                }
              }
              if (c == 'J')
              {
                if (n == 2)
                {
                  
                }
              }
              if (c == ';')
              {
                uint16_t m = 0;
                for (++j; j < 9; j++)
                {
                  if ('0' <= i[j] && i[j] <= '9')
                  {
                    m = m * 10 + (i[j] - '0');
                  }
                  else
                  {
                    c = i[j];
                    break;
                  }
                }
                if (c == 'H')
                {

                }
              }
              i += j + 1;
              continue;
            }
          }
        }
      }
    }
    gfx->fillRect(gfx->getCursorX(), gfx->getCursorY(), gfx->fontWidth(), gfx->fontHeight(), gfx->getTextStyle().fore_rgb888);
    return (i - buf);
  }

  mp_uint_t gfx_ioctl(mp_obj_t self, mp_uint_t request, uintptr_t arg, int *errcode)
  {
    return 0;
  }

  const font_obj_t gfx_font_0_obj = {{ &mp_type_object }, &m5gfx::fonts::Font0 };
  const font_obj_t gfx_font_2_obj = {{ &mp_type_object }, &m5gfx::fonts::Font2 };
  const font_obj_t gfx_font_4_obj = {{ &mp_type_object }, &m5gfx::fonts::Font4 };
  const font_obj_t gfx_font_6_obj = {{ &mp_type_object }, &m5gfx::fonts::Font6 };
  const font_obj_t gfx_font_7_obj = {{ &mp_type_object }, &m5gfx::fonts::Font7 };
  const font_obj_t gfx_font_8_obj = {{ &mp_type_object }, &m5gfx::fonts::Font8 };
  const font_obj_t gfx_font_DejaVu9_obj  = {{ &mp_type_object }, &m5gfx::fonts::DejaVu9  };
  const font_obj_t gfx_font_DejaVu12_obj = {{ &mp_type_object }, &m5gfx::fonts::DejaVu12 };
  const font_obj_t gfx_font_DejaVu18_obj = {{ &mp_type_object }, &m5gfx::fonts::DejaVu18 };
  const font_obj_t gfx_font_DejaVu24_obj = {{ &mp_type_object }, &m5gfx::fonts::DejaVu24 };

}
