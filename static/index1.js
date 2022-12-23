const SERVER_URL_DEV = "0.0.0.0";
formData = {}

const updateModels = async () => {
	return await axios.get(`http://${SERVER_URL_DEV}/user/update/A`).then(res => res.data)
}

const getAllArtistIds = async () => {
	return await axios.get(`http://${SERVER_URL_DEV}/user/artistIds`).then(res => res.data)
}

const getAllArtists = async () => {
	return await axios.get(`http://${SERVER_URL_DEV}/user`).then(res => res.data)
}

const getArtist = async (artistId) => {
	return await axios.get(`http://${SERVER_URL_DEV}/user/${artistId}`).then(res => res.data)
}

const getArtistMerch = async (artistId) => {
	return await axios.get(`http://${SERVER_URL_DEV}/user/${artistId}/merch`).then(res => res.data)
}

const updateMerch = async (transactions) => {
	return await axios.post(`http://${SERVER_URL_DEV}/user/${artistId}/merch`, transactions).then(res => res.data)
}

window.onload = async () => {
	const formJson = await fetch('static/formio.json').then(res => res.text())
	console.log(formJson)
	const form = await Formio.createForm(document.getElementById('formio'), JSON.parse(formJson));

	form.on('change', changed => {
		console.log(changed)
		form.submission.data.artistId = 'A'
		console.log(form.getComponent('artistId'))
		const merchIdComponent = form.getComponent('merchId')
		merchIdComponent.defaultSchema.data.values = [
			{value:'there', label: 'hi'},
		]
		merchIdComponent.redraw();
	})
}
