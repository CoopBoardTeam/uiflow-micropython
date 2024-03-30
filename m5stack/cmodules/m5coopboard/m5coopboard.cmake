# Create an INTERFACE library for our C module.
add_library(usermod_M5COOPBOARD INTERFACE)

# Add our source files to the lib
target_sources(usermod_M5COOPBOARD INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}/coopboard.c
)

# Add the current directory as an include directory.
target_include_directories(usermod_M5COOPBOARD INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}
    ${CMAKE_CURRENT_LIST_DIR}/../../managed_components/espressif__esp_tinyusb/include
    ${CMAKE_CURRENT_LIST_DIR}/../../managed_components/espressif__tinyusb/src
    # ${CMAKE_CURRENT_LIST_DIR}/../../components/i2c_pca9555/include
)

# Link our INTERFACE library to the usermod target.
target_link_libraries(usermod INTERFACE usermod_M5COOPBOARD)
