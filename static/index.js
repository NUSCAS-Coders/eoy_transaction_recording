const SERVER_URL_DEV = SERVER_URL + ":5000";
formData = {}

const handleADiscountTransaction = (form) => {
	const transactions = form.submission.data.merchandisesToTransact
	const aTransactions = transactions
		.filter(t => t.artistId.value === "A")
	
	const temp = []
	aTransactions.forEach(
		t => {
			if (["A1", "A2", "A3", "A4", "A5", "A6"].includes(t.merchId.value)) {
				for (var i = 0; i < t.qty.value; i++) {
					temp.push({...t, qty: {label: 1, value: 1}})
				}
			}
		}
	)

	console.log("T: ", transactions, temp)

	if (temp.length >= 4) {

		form.submission = {
			data: {
				merchandisesToTransact: [
					...form.submission.data.merchandisesToTransact.filter(
						t => t.artistId.value != 'A'
					),
					...temp.slice(0, 4).map(
						t => ({...t, price: {label: `${t.price.label} [Discounted: $1]`, value: t.price - 1}})
					),
					...temp.slice(4)
				]
			}
		}
		console.log("SUB: ", form.submission)
		throwToast("Injected discount for Artist A...")
	}
}

const handleTDiscountTransaction = (form) => {
	const transactions = form.submission.data.merchandisesToTransact
	const sTransactions = transactions
		.filter(t => t.artistId.value === "T")
	const totalCost = sTransactions.reduce((accum, curr) => curr.price.value * curr.qty.value + accum, 0)
	console.log("TOTAL COST: ", totalCost)
	if (totalCost >= 15 && totalCost < 30) {
		throwToast("Artist T goods exceed $15!")	
	} else if (totalCost >= 30) {
		throwToast("Artist T goods exceed $30!")	
	}
}

const updateModels = async (artistId=None) => {
	return await axios.get(`http://${SERVER_URL_DEV}/user/update/${artistId ?? ""}`).then(res => res.data)
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

const throwToast = async(message) => {
	Toastify({
		text: message,
		duration: 8000,
		newWindow: true,
		close: true,
		gravity: "top", // `top` or `bottom`
		position: "center", // `left`, `center` or `right`
		stopOnFocus: true, // Prevents dismissing of toast on hover
		style: {
			background: "linear-gradient(to right, #00b09b, #96c93d)",
		},
		onClick: function(){} // Callback after click
	}).showToast();
}

window.onload = async () => {
	var formTransactionJson = await fetch('static/submitTransaction.json').then(res => res.text())
	formTransactionJson = formTransactionJson.replaceAll("<SERVER_URL>", SERVER_URL)
	console.log(formTransactionJson)
	const formHistoryJson = await fetch('static/historyTransaction.json').then(res => res.text())
	const pastTransactions = await fetch('static/transactions.json').then(res => res.text())
	console.log("trans: ", pastTransactions)
	console.log(formTransactionJson)


	const formHistory = await Formio.createForm(document.getElementById('formioHistory'), JSON.parse(formHistoryJson));

	console.log(formHistory)
	formHistory.submission.data.curr = {}
	formHistory.submission = {
		data: {
			merchandisesToTransact: JSON.parse(pastTransactions)
		}
	}

	const formTransaction = await Formio.createForm(document.getElementById('formioTransaction'), JSON.parse(formTransactionJson));

	console.log(formTransaction)
	formTransaction.submission.data.curr = {}

	formTransaction.on('change', async changed => {
		console.log(changed)
		if (changed.state == 'submitted' || !changed?.changed) {
			return
		}
		const artistIdComponent = formTransaction.getComponent('artistId')
		const merchIdComponent = formTransaction.getComponent('merchId')
		const priceComponent = formTransaction.getComponent('price')
		const qtyComponent = formTransaction.getComponent('qty')
		const datetimeComponent = formTransaction.getComponent('datetime')
		console.log("DT: ", datetimeComponent)
		console.log(changed)
		datetimeComponent.setValue(new Date().toLocaleString('en-GB'));
		const changedCompKey = changed.changed.component.key

		switch(changedCompKey) {
			case 'artistId':
				Swal.fire({
					title: 'Retrieving user info...',
					didOpen: async () => {
						Swal.showLoading();
						await updateModels(changed.changed.value.value);
						Swal.close();
					},
					willClose: () => null
				})
			case 'merchId':
			case 'price':
			case 'qty':
				formTransaction.submission = {
					data: {
						...formTransaction.submission.data,
						[changedCompKey]: changed.changed.value.value
					}
				}
				break;
			case 'merchandisesToTransact':
				if (!formTransaction.submission.data.isHandledADiscount) {
					handleADiscountTransaction(formTransaction)
					handleTDiscountTransaction(formTransaction)
				}
				break;

			default:
				break;
		}
		console.log(formTransaction)
		console.log(formTransaction.getComponent('artistId'))

		console.log(formTransaction.submission)

	})

	formTransaction.on('error', async err => {
		console.log("ERR: ", err)
		Swal.fire({
			title: 'Error!',
			text: JSON.stringify(err),
			icon: 'error',
		})
	})

	formTransaction.on('submit', async submission => {
		console.log(submission)
		const formData = submission.data.merchandisesToTransact
		const transactions = formData.map(
			data => ({
				artistId: data.artistId,
				merchId: data.merchId,
				qty: data.qty,
				price: data.price,
				datetime: data.datetime
			})
		) 		
		Swal.fire({
			title: 'Submitting transaction...',
			didOpen: async () => {
				Swal.showLoading();
				await updateMerch(
					transactions
				).then(() => {
					Swal.fire({
						title: 'Success!',
						text: 'Wait for page to reload...',
						icon: 'success',
						timer: 1000,
						timerProgressBar: true
					}).then(() => 
						window.location.reload()
					)
				})
			},
			willClose: () => null
		})
	})
}
