with date_spine as (
    select
        dateadd(
            'day',
            row_number() over (order by null) - 1,
            '2023-01-01'::date
        ) as full_date
    from table(generator(rowcount => 1500))
),

-- filter must happen in a separate CTE; window functions can't be referenced
-- in WHERE within the same SELECT block in Snowflake
filtered as (
    select full_date
    from date_spine
    where full_date <= current_date()
)

select
    to_number(to_char(full_date, 'YYYYMMDD'))  as date_key,
    full_date,
    year(full_date)                             as year,
    quarter(full_date)                          as quarter,
    month(full_date)                            as month,
    monthname(full_date)                        as month_name,
    weekofyear(full_date)                       as week_of_year
from filtered
