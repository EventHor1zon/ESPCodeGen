
from string import Template


regmap_string = """
typedef struct {
    $contents
} $regmap_name;
"""

regmap_template = Template(regmap_string)

register_string = """ 
struct {
    union {
        uint8_t regbyte;
        struct {
            $contents
        } regbits;
    } value;
    uint8_t address;
    uint8_t default;
} $reg_name; 
"""

register_template = Template(register_string)


esp_get_string = """
esp_err_t ${drivername}_get_${param}($handlename dev, $vartype *var) {
    esp_err_t err = ESP_OK;
    *var = $handlename->$param;
    return err;
}
"""

esp_get_template = Template(esp_get_string)

esp_set_string = """
esp_err_t ${drivername}_set_${param}($handlename dev, $vartype *var) {
    esp_err_t err = ESP_OK;
    $vartype v = *var;

    if(v > $limit) {
        err = ESP_ERR_INVALID_ARG;
    }
    else {
        /** user code here **/
        v = (v << ${shift});

    }
    return err;
}
"""

esp_set_template = Template(esp_set_string)

