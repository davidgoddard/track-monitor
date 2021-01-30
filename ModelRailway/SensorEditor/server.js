const express = require('express');
const app = express();
const path = require('path');
const fs = require('fs');

// Parse JSON bodies (as sent by API clients)
app.use(express.json({limit: '50mb'}));
app.use(express.static('public'))

app.get('/references', (req, res) => {
	const testFolder = path.join(__dirname, '../TrackMonitor/ref/');
	const fs = require('fs');
	let files = []
	fs.readdirSync(testFolder).forEach(file => {
		files.push(file)
	});
	res.send(JSON.stringify(files))
})
app.post('/remove', (req, res) => {
	fs.unlinkSync('../TrackMonitor/ref/' + req.body.file, 'utf-8');
	res.sendStatus(200);
});
app.get('/layout', (req, res) => {
	const testFolder = path.join(__dirname, '../TrackMonitor/ref/');
	const fs = require('fs');
	let n = 0;
	fs.readdirSync(testFolder).sort().reverse().forEach(file => {
	if (fs.statSync(testFolder + file).isFile()) {
		if (file.endsWith('png')) {
      		if ( n == 0 ){
				console.log(file)
				res.sendFile(path.join(__dirname, '../TrackMonitor/ref/' + file));
				n ++;
			}
		}
	}
});
});
app.get('/ref/:path', (req, res) => {
	res.sendFile(path.join(__dirname, '../TrackMonitor/ref/' + req.params.path))
});
app.get('/config', (req, res) => {
	res.sendFile(path.join(__dirname, '../TrackMonitor/POI.json'))
});
app.post('/config', (req, res) => {
	fs.writeFileSync('../TrackMonitor/POI.json', JSON.stringify(req.body, null, 3), 'utf-8');
	console.log('Saved', req.body)
	res.sendStatus(200);
});
app.get('/restart', (req, res) => {
	console.log('restart')
})
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '/public', 'block_mapper.html'));
});

app.listen(80, () => {
	console.log('Sensor/Block Editor app server')
});
