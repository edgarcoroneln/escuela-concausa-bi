select cct, id_ciclo, count(*) as filas
from gold.predicciones
where modelo = 'ML-01'
group by cct, id_ciclo
having count(*) > 1
order by count(*) desc
limit 20;

select cct, id_ciclo, count(*) as filas
from gold.recomendaciones
group by cct, id_ciclo
having count(*) > 1
order by count(*) desc
limit 20;

select cct, id_ciclo, count(*) as filas
from gold.cubo_escuela_360
group by cct, id_ciclo
having count(*) > 1
order by count(*) desc
limit 20;

select cct, id_ciclo, count(distinct mlflow_run_id) as n_runs_distintos, count(*) as filas
from gold.predicciones
where modelo = 'ML-01'
group by cct, id_ciclo
having count(distinct mlflow_run_id) > 1
limit 20;
