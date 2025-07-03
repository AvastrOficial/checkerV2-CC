 let results = {
      live: [],
      die: [],
      unknown: []
    };

    async function validarTarjetas() {
      const btn = document.getElementById('validarBtn');
      const textarea = document.getElementById('ccList');
      const resultadosDiv = document.getElementById('resultados');
      const progressBarContainer = document.getElementById('progressBarContainer');
      const progressBar = document.getElementById('progressBar');

      const rawInput = textarea.value.trim();
      const lines = rawInput.split('\n').filter(l => l.includes('|'));

      if (lines.length === 0) {
        alert("No se encontraron tarjetas válidas.");
        return;
      }

      resultadosDiv.innerHTML = '';
      progressBarContainer.style.display = 'block';
      progressBar.style.width = '0%';
      btn.disabled = true;

      let liveCount = 0;
      let dieCount = 0;
      let unknownCount = 0;

      // Crear y añadir resumen inicial
      const resumen = document.createElement('div');
      resumen.className = 'resumen';
      resumen.id = 'resumenConteo';
      resumen.innerHTML = `
        <i class="fas fa-check-circle"></i> Live: <span id="liveCount">0</span>
        <i class="fas fa-times-circle"></i> Die: <span id="dieCount">0</span>
        <i class="fas fa-exclamation-circle"></i> Unknown: <span id="unknownCount">0</span>
        <i class="fas fa-calculator"></i> Total: <span id="totalCount">0</span>
      `;
      resultadosDiv.appendChild(resumen);

      for (let i = 0; i < lines.length; i++) {
        const tarjeta = lines[i].trim();

        try {
          const res = await fetch("Api Privada", {
            method: "POST",
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({
              data: tarjeta,
              charge: 'false'
            })
          });

          const data = await res.json();
          const div = document.createElement('div');
          div.className = 'result';

          if (data.code === 0) {
            div.classList.add('die');
            dieCount++;
            results.die.push(data.card?.card || tarjeta);
          } else if (data.code === 2) {
            div.classList.add('unknown');
            unknownCount++;
            results.unknown.push(data.card?.card || tarjeta);
          } else {
            liveCount++;
            results.live.push(data.card?.card || tarjeta);
          }

          div.innerHTML = `
<i class="fas fa-credit-card"></i> ${data.card?.card || tarjeta}
<i class="fas fa-chart-bar"></i> <b>Status:</b> ${data.status || 'N/A'} (${data.code})  
<i class="fas fa-comments"></i> <b>Mensaje:</b> ${data.message || 'Sin mensaje'}  
<i class="fas fa-building"></i> <b>Banco:</b> ${data.card?.bank || 'Desconocido'}  
<i class="fas fa-briefcase"></i> <b>Tipo:</b> ${data.card?.type || '?'} - ${data.card?.category || '?'}  
<i class="fas fa-tag"></i> <b>Marca:</b> ${data.card?.brand || 'N/A'}  
<i class="fas fa-globe"></i> <b>País:</b> ${data.card?.country?.name || 'N/A'} (${data.card?.country?.code || '-'}) ${data.card?.country?.emoji || ''}  
<i class="fas fa-money-bill-wave"></i> <b>Moneda:</b> ${data.card?.country?.currency || 'N/A'}
<i class="fas fa-map-marker-alt"></i> <b>Geo:</b> Lat: ${data.card?.country?.location?.latitude ?? '?'}, Lng: ${data.card?.country?.location?.longitude ?? '?'}
<i class="fas fa-check-circle"></i> Verificado con el bot <b>BSZCheker</b>
          `;
          resultadosDiv.appendChild(div);

        } catch (e) {
          const errorDiv = document.createElement('div');
          errorDiv.className = 'result die';
          errorDiv.innerText = `<i class="fas fa-times-circle"></i> Error al validar ${tarjeta}: ${e.message || 'Sin detalle'}`;
          resultadosDiv.appendChild(errorDiv);
          dieCount++;
          results.die.push(tarjeta);
        }

        // Actualizar resumen
        document.getElementById('liveCount').textContent = liveCount;
        document.getElementById('dieCount').textContent = dieCount;
        document.getElementById('unknownCount').textContent = unknownCount;
        document.getElementById('totalCount').textContent = liveCount + dieCount + unknownCount;

        progressBar.style.width = `${Math.round(((i + 1) / lines.length) * 100)}%`;
        await new Promise(r => setTimeout(r, 1000));
      }

      textarea.value = '';
      btn.disabled = false;
      setTimeout(() => {
        progressBarContainer.style.display = 'none';
        progressBar.style.width = '0%';
      }, 800);
    }

    function copiarResultados() {
      const allResults = [
        '<i class="fas fa-check-circle"></i> Live:\n' + results.live.join('\n'),
        '<i class="fas fa-times-circle"></i> Die:\n' + results.die.join('\n'),
        '<i class="fas fa-exclamation-circle"></i> Unknown:\n' + results.unknown.join('\n'),
        '<i class="fas fa-check-circle"></i> Verificado con el bot <b>BSZCheker</b>'
      ].join('\n\n');

      const textarea = document.createElement('textarea');
      textarea.value = allResults;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      alert("Resultados copiados al portapapeles.");
    }
