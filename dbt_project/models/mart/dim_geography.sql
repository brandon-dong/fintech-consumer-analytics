with source as (
    select distinct
        state,
        zip_code
    from {{ ref('stg_cfpb_complaints') }}
    where state is not null
),

final as (
    select
        hash(coalesce(state, ''), coalesce(zip_code, ''))::bigint as geography_key,
        state,
        zip_code
    from source
)

select * from final
