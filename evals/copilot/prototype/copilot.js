/* Spec 152 FR-2 / FR-3: the copilot prototype's page. Vanilla, Chrome on the desktop.
 *
 * Two sources: Microphone (getUserMedia) is the founder; Share (getDisplayMedia, the call's tab, the video dropped) is
 * the respondent. Rehearsal: one microphone, T switches which side the next turn belongs to. Per source an AnalyserNode
 * gives the level and a ScriptProcessorNode the samples: a turn opens after 150 ms above the threshold and closes after
 * 0.7 s below it; turns under 0.4 s are dropped. Each turn is encoded as a 16-bit mono WAV at the context's rate and
 * posted to the server the moment it is cut; the card never waits for a reply before the next turn can be cut, and the
 * server reads the turns in the order they arrive.
 *
 * The card is the UX page's: header, Now (question + frame pills), Heard, Filed, the key legend. It floats in a
 * Document Picture-in-Picture window (380 x 560). Every key works in whichever window holds the card.
 */
(function () {
  'use strict';

  var D = null;                 // /copilot.json: items, constants, the card
  var C = {};                   // the constants
  var items = {}, order = [];
  var card = null;              // the server's card (the newest rev seen)
  var seq = 0;                  // turns cut, both sides
  var inflight = {};            // seq -> {who, q_at, posted (ms), ended_at (s), keyed, failed}
  var walls = {};               // seq -> {wall s, parts}
  var shownBack = {};           // seq -> the page's shown_at, sent back on the next request
  var listening = true, autoPaused = false, lastTurnAt = Date.now();
  var rehearsal = false, side = 'founder';
  var askAgain = false;
  var lastClock = null;
  var pipWin = null;
  var ctx = null;
  var sources = {founder: null, them: null};
  var threshold = {founder: -48, them: -48};
  var startedAt = Date.now();

  var cp = document.getElementById('cp'), host = document.getElementById('host');
  var statusEl = document.getElementById('status'), logEl = document.getElementById('log');
  var micBtn = document.getElementById('mic'), shareBtn = document.getElementById('share');
  var rehBox = document.getElementById('rehearsal'), floatBtn = document.getElementById('float');

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c];
    });
  }
  function say(html, bad) { statusEl.innerHTML = html; statusEl.className = 'status' + (bad ? ' bad' : ''); }
  function nowS() { return Date.now() / 1000; }
  function keyCap(k) { return '<span class="key">' + esc(k) + '</span>'; }
  function qn(q) { return q && items[q] ? 'Q' + (order.indexOf(q) + 1) : ''; }

  // ------------------------------------------------------------------------------------------ the server

  function takeShown() { var s = shownBack; shownBack = {}; return s; }

  function acceptCard(c) { if (c && (!card || c.rev >= card.rev)) { card = c; listening = c.listening; } }

  function load() {
    fetch('/copilot.json').then(function (r) { return r.json(); }).then(function (j) {
      D = j; C = j.constants; card = j.card;
      j.items.forEach(function (it) { items[it.id] = it; order.push(it.id); });
      document.getElementById('runnote').innerHTML = 'Questionnaire <code>' + esc(j.questionnaire) + '</code> · ' +
        order.length + ' items · the log is <code>runs/' + esc(j.run) + '/</code>';
      say('Ready. Start the <b>Microphone</b>, then <b>Share</b> the call tab (or tick Rehearsal), then <b>Float</b>.');
      render();
    }).catch(function () { say('<b>The server did not answer.</b> Is <code>make copilot-prototype</code> running?', true); });
  }

  function postTurn(who, samples, rate, startedAtS, endedAtS) {
    seq += 1;
    var s = seq, wav = encodeWav(samples, rate);
    inflight[s] = {who: who, q_at: card ? card.current : null, posted: Date.now(), ended_at: endedAtS};
    var shown = takeShown(), sh = Object.keys(shown).map(function (k) { return k + ':' + shown[k].toFixed(3); });
    var qs = 'who=' + who + '&seq=' + s + '&started_at=' + startedAtS.toFixed(3) + '&ended_at=' + endedAtS.toFixed(3) +
      '&mode=' + (rehearsal ? 'rehearsal' : 'share') + (sh.length ? '&shown=' + sh.join(',') : '');
    render();
    fetch('/turn?' + qs, {method: 'POST', headers: {'Content-Type': 'audio/wav'}, body: wav})
      .then(function (r) { return r.json().then(function (j) { return {ok: r.ok, j: j}; }); })
      .then(function (res) {
        if (!res.ok) { if (inflight[s]) inflight[s].failed = true; say('<b>Turn ' + s + ' failed:</b> ' + esc(res.j.error) + '. File it by key, or carry on.', true); render(); return; }
        onEvent(res.j);
      })
      .catch(function () { if (inflight[s]) inflight[s].failed = true; render(); });
  }

  function onEvent(ev) {
    var f = inflight[ev.seq] || {};
    delete inflight[ev.seq];
    var shownAt = nowS();
    shownBack[ev.seq] = shownAt;
    var wall = f.ended_at ? shownAt - f.ended_at : null;
    walls[ev.seq] = {wall: wall, parts: ev.parts};
    lastClock = {seq: ev.seq, wall: wall, parts: ev.parts};
    if (ev.who === 'founder' && ev.heard) askAgain = false;
    acceptCard(ev.card);
    logRow(ev, wall);
    render();
  }

  function sendKey(k, extra) {
    var view = filedView();
    var body = {key: k, seq_of_turn: view.seq == null ? null : view.seq, at: nowS(), shown: takeShown()};
    if (extra) Object.keys(extra).forEach(function (x) { body[x] = extra[x]; });
    if (/^[0-6X]$/.test(k) && view.seq != null && inflight[view.seq]) inflight[view.seq].keyed = true;
    if (k === 'P' && !body.resume) listening = !listening;
    render();
    fetch('/key', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)})
      .then(function (r) { return r.json(); })
      .then(function (j) { acceptCard(j.card); if (j.applied === false && j.message) say(esc(j.message) + '.'); render(); })
      .catch(function () { say('<b>The key did not reach the server.</b>', true); });
  }

  // ------------------------------------------------------------------------------------------ the audio

  function audioCtx() {
    if (!ctx) {
      try { ctx = new AudioContext({sampleRate: C.sample_rate || 24000}); } catch (e) { ctx = new AudioContext(); }
    }
    if (ctx.state === 'suspended') ctx.resume();
    return ctx;
  }

  function rmsDb(buf) {
    var sum = 0;
    for (var i = 0; i < buf.length; i++) sum += buf[i] * buf[i];
    return 20 * Math.log10(Math.sqrt(sum / buf.length) + 1e-9);
  }

  function newCutter(source) {
    var open = false, above = 0, below = 0, chunks = [], pre = [], preLen = 0, who = null, startS = 0, endS = 0;
    var MAX_TURN_S = 90, PRE_S = 0.3;
    function close(rate) {
      var total = 0; chunks.forEach(function (c) { total += c.length; });
      var dur = endS - startS, samples = new Float32Array(total), off = 0;
      chunks.forEach(function (c) { samples.set(c, off); off += c.length; });
      open = false; chunks = []; below = 0; above = 0;
      if (dur >= C.turn_min_s) postTurn(who, samples, rate, startS, endS);
    }
    return {
      feed: function (x, lvl, rate) {
        var dt = x.length / rate, t = nowS();
        var loud = lvl > threshold[source];
        meter(source, lvl, loud && listening);
        if (!listening) { open = false; chunks = []; pre = []; preLen = 0; above = 0; return; }
        if (!open) {
          pre.push(x); preLen += x.length;
          while (pre.length > 1 && preLen - pre[0].length > rate * PRE_S) preLen -= pre.shift().length;
          above = loud ? above + dt : 0;
          if (above >= C.turn_open_s) {
            open = true; chunks = pre; pre = []; preLen = 0; below = 0;
            startS = t - above; endS = t;
            who = rehearsal ? side : source;
            lastTurnAt = Date.now(); autoPaused = false;
          }
        } else {
          chunks.push(x);
          if (loud) { below = 0; endS = t; } else { below += dt; }
          if (below >= C.turn_end_hold_s || t - startS > MAX_TURN_S) close(rate);
        }
      }
    };
  }

  function attach(stream, source) {
    var c = audioCtx();
    var src = c.createMediaStreamSource(stream);
    var an = c.createAnalyser(); an.fftSize = 2048;
    var proc = c.createScriptProcessor(2048, 1, 1);
    var mute = c.createGain(); mute.gain.value = 0;
    src.connect(an); src.connect(proc); proc.connect(mute); mute.connect(c.destination);
    var cutter = newCutter(source), lvlBuf = new Float32Array(an.fftSize), lastTick = 0;
    proc.onaudioprocess = function (e) {
      an.getFloatTimeDomainData(lvlBuf);
      cutter.feed(new Float32Array(e.inputBuffer.getChannelData(0)), rmsDb(lvlBuf), c.sampleRate);
      if (Date.now() - lastTick > 250) { lastTick = Date.now(); tick(); }   // the audio keeps the card's clock
    };
    sources[source] = {stream: stream, nodes: [src, an, proc, mute]};
  }

  function detach(source) {
    var s = sources[source];
    if (!s) return;
    s.stream.getTracks().forEach(function (t) { t.stop(); });
    s.nodes.forEach(function (n) { try { n.disconnect(); } catch (e) { /* already */ } });
    s.nodes[2].onaudioprocess = null;
    sources[source] = null;
    meter(source, -100, false);
  }

  function meter(source, lvl, loud) {
    var el = document.getElementById('lvl-' + source);
    if (!el) return;
    el.style.width = Math.max(0, Math.min(100, (lvl + 70) / 55 * 100)) + '%';
    el.className = loud ? 'loud' : '';
  }

  function encodeWav(samples, rate) {
    var buf = new ArrayBuffer(44 + samples.length * 2), v = new DataView(buf);
    function str(o, s) { for (var i = 0; i < s.length; i++) v.setUint8(o + i, s.charCodeAt(i)); }
    str(0, 'RIFF'); v.setUint32(4, 36 + samples.length * 2, true); str(8, 'WAVE');
    str(12, 'fmt '); v.setUint32(16, 16, true);
    v.setUint16(20, 1, true);                 // PCM
    v.setUint16(22, 1, true);                 // mono
    v.setUint32(24, rate, true);
    v.setUint32(28, rate * 2, true);          // bytes a second
    v.setUint16(32, 2, true);                 // block align
    v.setUint16(34, 16, true);                // 16-bit
    str(36, 'data'); v.setUint32(40, samples.length * 2, true);
    for (var i = 0, o = 44; i < samples.length; i++, o += 2) {
      var x = Math.max(-1, Math.min(1, samples[i]));
      v.setInt16(o, x < 0 ? x * 0x8000 : x * 0x7FFF, true);
    }
    return new Blob([buf], {type: 'audio/wav'});
  }

  function startMic() {
    if (sources.founder) { detach('founder'); micBtn.classList.remove('on'); micBtn.textContent = 'Microphone'; render(); return; }
    navigator.mediaDevices.getUserMedia({audio: {echoCancellation: true, noiseSuppression: true, autoGainControl: true}})
      .then(function (stream) {
        attach(stream, 'founder');
        micBtn.classList.add('on'); micBtn.textContent = 'Microphone · on';
        say(rehearsal ? 'Rehearsal: one microphone. Press <b>T</b> before you speak as the other side.' :
          'Microphone on: that is you. Now <b>Share</b> the call tab for the other side.');
        render();
      })
      .catch(function (err) { say('<b>Microphone:</b> ' + esc(err.name) + ' -- allow the microphone for this page and press it again.', true); });
  }

  function startShare() {
    if (sources.them) { detach('them'); shareBtn.classList.remove('on'); shareBtn.textContent = 'Share the call tab'; render(); return; }
    navigator.mediaDevices.getDisplayMedia({audio: true, video: true})
      .then(function (stream) {
        if (!stream.getAudioTracks().length) {
          stream.getTracks().forEach(function (t) { t.stop(); });
          say('<b>No audio came with that share.</b> Share again, pick the call\'s <b>Chrome tab</b>, and keep <i>Also share tab audio</i> on.', true);
          return;
        }
        stream.getVideoTracks().forEach(function (t) { t.stop(); stream.removeTrack(t); });
        stream.getAudioTracks()[0].addEventListener('ended', function () {
          detach('them'); shareBtn.classList.remove('on'); shareBtn.textContent = 'Share the call tab';
          say('The tab share ended. Share again to hear the other side.', true);
        });
        attach(stream, 'them');
        shareBtn.classList.add('on'); shareBtn.textContent = 'Sharing · on';
        say('Sharing the call tab: that is the respondent. Press <b>Float</b>, click the card once, and start.');
        render();
      })
      .catch(function (err) { say('<b>Share:</b> ' + esc(err.name) + '.', true); });
  }

  // ------------------------------------------------------------------------------------------ the card

  function filedView() {
    var stuck = null, newest = null, row = card && card.filed_row;
    var rowSeq = row && row.seq != null ? row.seq : -1;
    Object.keys(inflight).map(Number).sort(function (a, b) { return a - b; }).forEach(function (s) {
      var t = inflight[s];
      if (t.who !== 'them' || t.keyed) return;
      var age = (Date.now() - t.posted) / 1000;
      if ((t.failed || age >= C.give_up_s) && !stuck) stuck = {seq: s, t: t, age: age};
      if (s > rowSeq) newest = {seq: s, t: t, age: age};
    });
    if (stuck) return {kind: 'stuck', seq: stuck.seq, q: stuck.t.q_at, age: stuck.age, failed: stuck.t.failed};
    if (newest) return {kind: 'working', seq: newest.seq, q: newest.t.q_at, age: newest.age};
    if (row) return {kind: row.kind, seq: row.seq, q: row.q, row: row};
    return {kind: 'none', seq: null, q: null};
  }

  function optsHtml(q, on) {
    var it = items[q];
    if (!it) return '';
    var h = (it.options || []).map(function (o, i) {
      return '<div class="opt' + (on && on.indexOf(i + 1) >= 0 ? ' on' : '') + '">' + keyCap(i + 1) + '<span>' + esc(o) + '</span></div>';
    }).join('');
    if (it.escape) h += '<div class="opt">' + keyCap(0) + '<span>' + esc(it.escape) + '</span></div>';
    h += '<div class="opt">' + keyCap('X') + '<span>Not an answer, keep as a note</span></div>';
    return '<div class="opts">' + h + '</div>';
  }

  function framePills(pills, miss) {
    if (!pills || !pills.length) return '';
    return '<div class="frame">' + pills.map(function (p) {
      return '<span class="' + (miss && miss.indexOf(p) >= 0 ? 'miss' : '') + '">' + esc(p) + '</span>';
    }).join('') + '</div>';
  }

  function secs(seqN) {
    var w = walls[seqN];
    return w && w.wall != null ? ' · ' + w.wall.toFixed(1) + ' s' : '';
  }

  function filedHtml(v) {
    var cls = '', k = 'Filed', b = '', p = '', extra = '';
    var Q = qn(v.q), f = v.row && v.row.filing;
    if (card && card.done && v.kind !== 'stuck' && v.kind !== 'working') {
      var c = card.counts;
      return '<div class="filed sure"><span class="k">Done · ' + (c.filed_by_box + c.filed_by_key + c.filed_as_notes) + ' of ' + c.items +
        ' filed</span><b>Thank them</b><p>' + c.filed_by_box + ' filed by the box, ' + c.filed_by_key + ' by you, ' +
        (c.filed_as_notes + c.own_notes) + ' notes. The session log is in the run folder.</p></div>';
    }
    switch (v.kind) {
      case 'working':
        cls = 'working';
        if (v.age < C.still_working_s) { k = 'Filed · working'; b = '<span class="spin"></span>Reading the answer'; p = 'Carry on. It lands in a few seconds.'; }
        else { k = 'Filed · ' + Q + ' · working ' + Math.floor(v.age) + ' s'; b = '<span class="spin"></span>Still working'; p = 'still working, carry on'; }
        break;
      case 'stuck':
        cls = 'hand';
        k = 'Filed · ' + Q + (v.failed ? ' · no reply' : ' · stuck for ' + Math.floor(v.age) + ' s');
        b = v.failed ? 'No reply' : 'Still working';
        p = 'File it yourself, or move on: it files itself if it lands first.';
        extra = optsHtml(v.q, []);
        break;
      case 'sure': case 'likely': case 'keyed':
        cls = v.kind === 'likely' ? 'likely' : 'sure';
        k = 'Filed · ' + Q + ' · ' + (v.kind === 'keyed' ? 'by you' : v.kind) + secs(v.seq);
        b = esc(f ? f.label : '');
        if (v.kind === 'likely') {
          extra = framePills(f && f.frame, f && f.frame_missing) + optsHtml(v.q, (f && f.option && f.option.picks) || []);
        } else {
          extra = framePills(f && f.frame, f && f.frame_missing);
          p = keyCap('Z') + ' undo &nbsp;' + keyCap('X') + ' note' + (f && f.frame_missing && f.frame_missing.length ? ' &nbsp;· asked without the amber words' : '');
        }
        break;
      case 'unsure':
        cls = 'hand'; k = 'Filed · ' + Q + ' · unsure' + secs(v.seq); b = 'I did not catch that'; extra = optsHtml(v.q, []);
        break;
      case 'heard_nothing':
        cls = 'hand'; k = 'Filed · ' + Q + ' · heard nothing'; b = 'Ask again'; p = keyCap('R') + ' shows the question to read, or press a number.';
        extra = optsHtml(v.q, []);
        break;
      case 'undone':
        cls = 'hand'; k = 'Filed · ' + Q + ' · undone'; b = 'Nothing filed'; extra = optsHtml(v.q, []);
        break;
      case 'kept_note':
        k = 'Filed · note under ' + Q; b = 'Not an answer'; p = 'Their reply is kept as a note. ' + keyCap('Z') + ' undo';
        break;
      case 'note':
        k = 'Filed · note under ' + Q;
        b = v.row && v.row.verdict === 'follow_up' ? 'Their reply to your own question' : 'Not an answer';
        p = 'Kept as a note, not as an answer.';
        break;
      case 'own_question':
        k = 'Filed · note under ' + (Q || 'the opening'); b = 'Your own question';
        p = 'Your own question, kept as a note under ' + (Q || 'the opening') + ', with their reply. No pause.';
        break;
      default:
        return '<div class="filed"><span class="k">Filed</span><p>Nothing filed yet.</p></div>';
    }
    return '<div class="filed ' + cls + '"><span class="k">' + k + '</span><b>' + b + '</b>' + (p ? '<p>' + p + '</p>' : '') + extra + '</div>';
  }

  function nowHtml() {
    var q = card && card.current, it = items[q] || items[order[0]];
    if (!it) return '<div class="q"><span class="k">Now</span><p>Loading…</p></div>';
    if (card && card.done) return '<div class="q"><span class="k">Now</span><p>All ' + order.length + ' asked. Thank them and close the box.</p></div>';
    var flagged = q && card.flags && Object.prototype.hasOwnProperty.call(card.flags, q);
    var miss = flagged ? card.flags[q] : [];
    var reading = Object.keys(inflight).some(function (s) { return inflight[s].who === 'founder'; });
    var label = 'Now' + (q ? '' : ' · not asked yet');
    var cls = 'q';
    if (!listening) { label = 'Paused · ' + keyCap('P') + ' to listen again'; cls += ' paused'; }
    else if (autoPaused) { label = 'Paused · five minutes of silence'; cls += ' paused'; }
    else if (flagged) { label = 'Now · asked differently? ' + keyCap('F') + ' keep · ' + keyCap('X') + ' note'; cls += ' flag'; }
    if (q && card.note_next && card.note_next.indexOf(q) >= 0) label += ' · next reply kept as a note';
    if (reading) label += ' · <span class="spin"></span>reading you';
    var body;
    if (askAgain) {
      var sp = it.spoken || {};
      cls += ' ask';
      body = '<p>' + esc((sp.anchor ? sp.anchor + ' ' : '') + (sp.stem || it.question)) + '</p>' +
        [sp.countLine, sp.optionsLine, sp.escapeLine].filter(Boolean).map(function (l) { return '<p class="line">' + esc(l) + '</p>'; }).join('');
      label = 'Ask again · read it as written · ' + keyCap('R') + ' to close';
    } else {
      body = '<p>' + esc(it.question) + '</p>';
    }
    return '<div class="' + cls + '"><span class="k">' + label + '</span>' + body +
      framePills(card && card.frames ? card.frames[it.id] : [], miss) + '</div>';
  }

  function heardHtml() {
    var h = card && card.heard_row;
    if (!h) return '<div class="heard"><i>nothing heard yet</i></div>';
    var who = h.who === 'founder' ? 'You' : 'Them';
    return '<div class="heard"><b>' + who + '</b> · ' + (h.heard ? esc(h.heard) : '<i>heard nothing</i>') + '</div>';
  }

  function render() {
    if (!D) return;
    var v = filedView();
    var anyInflight = Object.keys(inflight).length > 0;
    var dot = !listening ? 'paused' : (card.done ? 'done' : (/^(stuck|unsure|heard_nothing|undone)$/.test(v.kind) ? 'hand' : (anyInflight ? 'working' : 'listening')));
    var handled = Object.keys(card.filings || {}).length;
    var prog = '<span class="prog">' + order.map(function (id) { return '<i class="' + (card.filings[id] ? 'on' : '') + '"></i>'; }).join('') + '</span>';
    var el = Math.floor((Date.now() - startedAt) / 1000);
    var clock = String(Math.floor(el / 60)).padStart(2, '0') + ':' + String(el % 60).padStart(2, '0');
    var sub = (card.done ? 'Finished' : (card.current ? 'Question ' + card.n + ' of ' + card.N : 'No question yet · ' + order.length + ' to ask')) +
      ' · ' + handled + ' filed' + (rehearsal ? ' · next turn: <b>' + (side === 'founder' ? 'You' : 'Them') + '</b> ' + keyCap('T') : '') + ' · ' + clock;
    var h = '<div class="h"><span class="dot ' + dot + '"></span><b>Keel copilot</b>' + prog + '<small>' + sub + '</small></div>';
    var split = lastClock && lastClock.wall != null ? lastClock.wall.toFixed(1) + ' s · t ' + lastClock.parts.transcribe.toFixed(1) +
      ' · c ' + lastClock.parts.classify.toFixed(1) + (lastClock.parts.queue > 0.05 ? ' · q ' + lastClock.parts.queue.toFixed(1) : '') : 'Stack 1 · gpt-transcribe + Haiku';
    var foot = '<div class="foot"><span>' + keyCap('R') + ' ask again &nbsp;' + keyCap('→') + ' next &nbsp;' + keyCap('P') + ' pause</span><span>' + split + '</span></div>';
    cp.innerHTML = h + nowHtml() + heardHtml() + filedHtml(v) + foot;
  }

  function tick() {
    if (D && listening && !autoPaused && Date.now() - lastTurnAt > C.silence_pause_s * 1000) autoPaused = true;
    render();
  }

  function logRow(ev, wall) {
    var it = items[ev.q];
    var read = (ev.q ? qn(ev.q) : '—') + (ev.verdict ? ' · ' + ev.verdict : '');
    if (ev.option && it) {
      var o = ev.option, lab = o.picks ? o.picks.map(function (n) { return (it.options || [])[n - 1]; }).join('; ') :
        (o.escape ? it.escape : (o.value != null ? o.value + (it.unit ? ' ' + it.unit : '') : (o.unclear ? 'unclear' : '')));
      read += ' · ' + lab;
    }
    if (ev.tier) read += ' · ' + ev.tier;
    if (ev.late) read += ' · late';
    var p = ev.parts || {};
    var tr = document.createElement('tr');
    tr.innerHTML = '<td class="n">' + ev.seq + '</td><td>' + (ev.who === 'founder' ? 'You' : 'Them') + '</td><td>' +
      (ev.heard ? esc(ev.heard) : '<i>heard nothing</i>') + '</td><td>' + esc(read) + '</td><td class="n">' +
      (wall != null ? wall.toFixed(1) + ' s' : '') + '</td><td class="n">t ' + (p.transcribe || 0).toFixed(1) + ' · c ' +
      (p.classify || 0).toFixed(1) + (p.queue > 0.05 ? ' · q ' + p.queue.toFixed(1) : '') + '</td>';
    logEl.insertBefore(tr, logEl.firstChild);
  }

  // ------------------------------------------------------------------------------------------ the keys

  function onKey(e) {
    var t = e.target;
    if (t && /^(INPUT|SELECT|TEXTAREA)$/.test(t.tagName) && e.key !== 'Escape') return;
    if (e.metaKey || e.ctrlKey || e.altKey || !D) return;
    var k = e.key, low = k.length === 1 ? k.toLowerCase() : k;
    if (/^[0-6]$/.test(k)) sendKey(k);
    else if (low === 'x') sendKey('X');
    else if (low === 'f') sendKey('F');
    else if (low === 'z') sendKey('Z');
    else if (low === 'p') {
      if (autoPaused && listening) { autoPaused = false; lastTurnAt = Date.now(); sendKey('P', {resume: true}); }
      else sendKey('P');
    }
    else if (k === 'ArrowRight') { askAgain = false; sendKey('ArrowRight'); }
    else if (k === ' ') { askAgain = false; sendKey('Space'); }
    else if (k === 'ArrowLeft') { askAgain = false; sendKey('ArrowLeft'); }
    else if (low === 'r') { askAgain = !askAgain; render(); logKey('R'); }
    else if (low === 't') { if (rehearsal) side = side === 'founder' ? 'them' : 'founder'; render(); logKey('T'); }
    else if (k === 'Escape') { toggleFloat(); logKey('Escape'); }
    else return;
    e.preventDefault();
  }

  function logKey(k) {
    fetch('/key', {method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({key: k, seq_of_turn: null, at: nowS(), shown: takeShown()})}).catch(function () {});
  }

  // ------------------------------------------------------------------------------------------ Picture-in-Picture

  function toggleFloat() {
    if (pipWin) { pipWin.close(); return; }
    if (!('documentPictureInPicture' in window)) {
      say('<b>This browser has no Document Picture-in-Picture.</b> Use Chrome 116 or newer on a desktop.', true);
      return;
    }
    documentPictureInPicture.requestWindow({width: 380, height: 560}).then(function (w) {
      pipWin = w;
      [].slice.call(document.styleSheets).forEach(function (ss) {
        try {
          var st = w.document.createElement('style');
          st.textContent = [].slice.call(ss.cssRules).map(function (r) { return r.cssText; }).join('\n');
          w.document.head.appendChild(st);
        } catch (err) { /* a sheet we cannot read */ }
      });
      w.document.title = 'Keel copilot';
      w.document.body.className = 'pip';
      w.document.body.appendChild(cp);
      host.className = 'host away';
      host.textContent = 'The card is floating. Esc, or close its window, to bring it back.';
      w.document.addEventListener('keydown', onKey);
      w.addEventListener('pagehide', function () {
        host.className = 'host'; host.textContent = ''; host.appendChild(cp);
        pipWin = null; floatBtn.textContent = 'Float'; render();
      });
      floatBtn.textContent = 'Bring it back';
      say('<b>Floating</b> at ' + w.innerWidth + ' × ' + w.innerHeight + '. Click the card once so it takes the keys.');
      render();
    }).catch(function (err) { say('<b>Chrome refused the window:</b> ' + esc(err.name) + ' -- ' + esc(err.message), true); });
  }

  // ------------------------------------------------------------------------------------------ wiring

  ['founder', 'them'].forEach(function (s) {
    var input = document.getElementById('thr-' + s), mark = document.getElementById('thr-mark-' + s);
    function show() { threshold[s] = Number(input.value); mark.style.left = ((threshold[s] + 70) / 55 * 100) + '%'; }
    input.value = threshold[s]; show();
    input.addEventListener('input', show);
    input.addEventListener('change', function () { input.blur(); });
  });
  // a clicked control gives the focus back, so Space and the digits reach the card, not the button
  function andBlur(fn) { return function (e) { e.currentTarget.blur(); fn(); }; }
  micBtn.addEventListener('click', andBlur(startMic));
  shareBtn.addEventListener('click', andBlur(startShare));
  floatBtn.addEventListener('click', andBlur(toggleFloat));
  rehBox.addEventListener('change', function () {
    rehBox.blur();
    rehearsal = rehBox.checked;
    if (rehearsal && sources.them) startShare();          // one microphone: stop the share
    shareBtn.disabled = rehearsal;
    side = 'founder';
    render();
  });
  document.addEventListener('keydown', onKey);
  setInterval(tick, 250);
  load();
})();
