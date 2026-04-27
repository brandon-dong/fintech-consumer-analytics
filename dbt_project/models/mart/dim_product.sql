with source as (
    select distinct
        product,
        sub_product
    from {{ ref('stg_cfpb_complaints') }}
    where product is not null
),

final as (
    select
        hash(coalesce(product, ''), coalesce(sub_product, ''))::bigint as product_key,
        product                                                          as product_name,
        sub_product                                                      as product_category
    from source
)

select * from final
