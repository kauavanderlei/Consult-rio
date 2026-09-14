  function mudarPagina(id, botao){
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById('page-' + id).classList.add('active');

    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    botao.classList.add('active');
  }

  function alternarFormPaciente(){
    document.getElementById('form-paciente').classList.toggle('hidden');
  }