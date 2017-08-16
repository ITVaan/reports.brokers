set @t = -1;
CALL sp_check_tender('68072d2ab3e54b1e941cab880d9f839e', @t);
select @t;