SET SEARCH_PATH TO core;

/* 1. Identificar quais são os canais patrocinados e os valores de patrocínio pagos por empresa.
   SE UMA EMPRESA FEZ MAIS DE UM PATROCINIO PARA UM CANAL, PRECISA AGRUPAR?
   */
SELECT * FROM CANAISPATROCINADOSEMPRESA();

/*2. Descobrir de quantos canais cada usuário é membro e a soma do valor desembolsado por
usuário por mês.
  // DEVE CONSIDERAR USUARIOS SEM INSCRIÇÃO?
  */
SELECT * FROM GASTOMEMBRESIA();

/* 3. Listar e ordenar os canais que já receberam doações e a soma dos valores recebidos em
doação.
   SE É VALOR RECEBIDO ENTÃO O STATUS_PAGAMENTO TEM QUE SER CONCLUIDO? */
SELECT * FROM DOACOESCANAL();

/* 4. Listar a soma das doações geradas pelos comentários que foram lidos por vídeo.   */

-- Vale a pena adicionar a coluna "coment_on" na view "vw_faturamento_doacao" ?
SELECT * FROM DOACOESCOMENTARIOSLIDOS();

/* 5. Listar e ordenar os k canais que mais recebem patrocínio e os valores recebidos.
   usar o k = 5 por enquanto*/

SELECT * FROM MAIORPATROCINIO(5);

/* 6. Listar e ordenar os k canais que mais recebem aportes de membros e os valores recebidos.
   k=5 */
SELECT * FROM MAIORAPOIOMEMBROS(5);

/* 7. Listar e ordenar os k canais que mais receberam doações considerando todos os vídeos.
  k = 5  */

SELECT * FROM MAISDOACOES(5);

/* 8. Listar os k canais que mais faturam (Patrocínio + Membros + Doações). k=5 */
    /* uso de left join para pegar os casos que nao tem */
SELECT * FROM MAIORFATURAMENTO(5);
