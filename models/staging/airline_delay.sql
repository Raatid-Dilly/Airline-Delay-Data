{{ config(materialized='view') }}

select 
-- identifiers
    cast(year as integer) as year,
    {{ get_month('month') }} as month,
    city,
    {{ get_state_name('state') }} as state,
    carrier as carrier_code,
    carrier_name,
    airport as airport_code,
    airport_name,

--flights info
    cast(arr_flights as numeric) as arr_flights,
    cast(arr_del15 as numeric) as arr_delays_ct,
    cast(carrier_ct as numeric) as carrier_del_ct,
    cast(weather_ct as numeric) as weather_del_ct,
    cast(nas_ct as numeric) as nas_del_ct,
    cast(security_ct as numeric) as security_del_ct,
    cast(late_aircraft_ct as numeric) as late_aircraft_ct,
    cast(arr_cancelled as numeric) as arr_cancelled,
    cast(arr_diverted as numeric) as arr_diverted,

--flight minutes info
    cast(arr_delay as numeric) as arr_delay_mins,
    cast(carrier_delay as numeric) as carrier_del_mins,
    cast(weather_delay as numeric) as weather_del_mins,
    cast(nas_delay as numeric) as nas_del_mins,
    cast(security_delay as numeric) as security_del_mins,
    cast(late_aircraft_delay as numeric) as late_aircraft_del_mins

from {{ source('staging', 'flights_delay_external_table') }}
-- dbt build --m <model.sql> --var 'is_test_run: false'
{% if var('is_test_run', default=true) %}

    limit 100

{% endif %}