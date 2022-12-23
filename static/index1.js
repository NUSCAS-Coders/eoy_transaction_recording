const SERVER_URL_DEV = "0.0.0.0:5000";
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
	return await axios.post(`http://${SERVER_URL_DEV}/user/merch`, transactions).then(res => res.data)
}

window.onload = async () => {
	const formJson = await fetch('static/formio.json').then(res => res.text())
	console.log(formJson)
	const form = await Formio.createForm(document.getElementById('formio'), JSON.parse(formJson));
	form.submission.data.curr = {}
	form.on('change', changed => {
		console.log(changed)
		if (changed.state == 'submitted') {
			return
		}
		const artistIdComponent = form.getComponent('artistId')
		const merchIdComponent = form.getComponent('merchId')
		const priceComponent = form.getComponent('price')
		const qtyComponent = form.getComponent('qty')
		const changedCompKey = changed.changed.component.key 
		switch(changedCompKey) {
			case 'artistId':
				form.submission.data.curr[changedCompKey] = changed.changed.value.value
				break;
			case 'merchId':
				form.submission.data.curr[changedCompKey] = changed.changed.value.value
				break;
			case 'price':
				form.submission.data.curr[changedCompKey] = changed.changed.value.value
				break;
			case 'qty':
				form.submission.data.curr[changedCompKey] = changed.changed.value.value
				break;
		}
		console.log(form.getComponent('artistId'))
	})

	form.on('submit', async submission => {
		console.log(submission)
		const formData = submission.data.merchandisesToTransact
		const transactions = formData.map(
			data => ({
				artistId: data.artistId.value,
				merchId: data.merchId.value,
				qty: data.qty.value,
				price: data.price.value
			})
		) 		
		await updateMerch(
			transactions
		).then(() => {
				window.location.reload()
			}
		)
	})
}
