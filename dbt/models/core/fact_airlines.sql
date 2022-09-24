{{ config(materialized='table') }}

select * from {{ ref('airline_delay') }}