/**
 * Javascript file to accompany the HTML file: index.html.
 *
 *
 */

/**
 * Converts floats to currency value for display purpose.
 */
const floatToCurrency = (input) => {
	// Create our number formatter.
	const formatter = new Intl.NumberFormat('en-US', {
		style: 'currency',
		currency: 'USD',

		// These options are needed to round to whole numbers if that's what you want.
		//minimumFractionDigits: 0, // (this suffices for whole numbers, but will print 2500.10 as $2,500.1)
		//maximumFractionDigits: 0, // (causes 2500.99 to be printed as $2,501)
	});
	return formatter.format(input)
}

const currencyToFloat = (input) => {
	var currency = "$1,123,456.00";
	var number = Number(currency.replace(/[^0-9\.]+/g,""));
	return number;
}

/**
 * Handles Discount conditions for artist A.
 * If 4 of any of A1, A2, A3, A4, A5 and A6 are bought, apply a $1 discount to all items.
 * TODO: Represent this on google sheet to interpret on server.
 */
const handleADiscountTransaction = (form) => {
	// Retrieve saved data, which are not necessarily submitted.
	const transactions = form.submission.data.merchandisesToTransact

	// Filter by Artist A.
	const aTransactions = transactions
		.filter(t => t.artistId.value === "A")

	const temp = []
	const notTemp = []

	// Filter relevant merch.
	aTransactions.forEach(
		t => {
			if (["A1", "A2", "A3", "A4", "A5", "A6"].includes(t.merchId.value)) {
				// To assist computation, unspool it to single qty merch entries.
				for (var i = 0; i < t.qty.value; i++) {
					temp.push({...t, qty: {label: 1, value: 1}})
				}
			} else {
				notTemp.push(t)
			}
		}
	)

	console.log("T: ", transactions, temp)

	// If four of relevant merch is bought, execute discount.
	if (temp.length >= 4) {
		setsOfDiscount = Math.floor(temp.length / 4) * 4

		// Direct assignment to submission attribute is the only way to trigger form change.
		form.submission = {
			data: {
				merchandisesToTransact: [
					// Assign back non-relevant artist entries
					...form.submission.data.merchandisesToTransact.filter(
						t => t.artistId.value != 'A'
					),
					// Assign the discounted merches of relevance
					...temp.slice(0, setsOfDiscount).map(
						t => ({
							...t, 
							price: {
								label: `<span> ${floatToCurrency((t.price._value ?? t.price.value) - 1)} <span class=\"badge badge-info\">Discount</span> </span>`, 
								value: t.price.value - 1,
								_label: t.price._label ?? t.price.label,
								_value: t.price._value ?? t.price.value
							}
						})
					),
					// Assign back non-relevant merch of artist A.
					...temp.slice(setsOfDiscount).map(
						t => ({
							...t,
							price: {
								label: t.price._label ?? t.price.label,
								value: t.price._value ?? t.price.value
							}
						})
					),
					...notTemp
				]
			}
		}
		//console.log("SUB: ", form.submission)
		throwToast("Injected discount for Artist A...")
		return true
	} else {
		form.submission = {
			data: {
				merchandisesToTransact: [
					// Assign back non-relevant artist entries
					...form.submission.data.merchandisesToTransact.filter(
						t => t.artistId.value != 'A'
					),
					// Assign back non-relevant merch of artist A.
					...aTransactions.map(
						t => ({
							...t,
							price: {
								label: t.price._label ?? t.price.label,
								value: t.price._value ?? t.price.value
							}
						})
					)
				]
			}
		}
		return false
	}
}

/**
 * Handles Discount conditions for artist T.
 * Send notification if >$15 or >$30 of merch from this artist is purchased.
 * The operator should then give away freebies.
 * TODO: Represent this on google sheet to interpret on server.
 */
const handleTDiscountTransaction = async (form) => {
	const transactions = form.submission.data.merchandisesToTransact
	const sTransactions = transactions
		.filter(t => t.artistId.value === "T")
	const totalCost = sTransactions.reduce((accum, curr) => curr.price.value * curr.qty.value + accum, 0)
	console.log("TOTAL COST: ", totalCost)
	if (totalCost >= 15 && totalCost < 30) {
		// Trigger select prompt
		const { value: merchId } = await Swal.fire({
			title: 'Choose giveaway freebie!',
			input: 'select',
			inputOptions: {
				'Merch': {
					'T20': "Pochita",
					'T15': "GenshinGuy",
					'T18': "GenshinGirl"
				},
			},
			inputPlaceholder: 'Freebie...',
			showCancelButton: true,
			inputValidator: (value) => {
				return new Promise((resolve) => {
					resolve()
				})
			}
		})
		form.submission = {
			data: {
				merchandisesToTransact: [
					...form.submission.data.merchandisesToTransact,
					...await Promise.all([merchId].map(
						async m => ({
							... await getSingleArtistMerch('T', m), 
							artistId: {label: "T - Shan", value: "T"}, 
							qty: 1, 
							price: {label: "Giveaway", value: 0}, 
							datetime: new Date().toLocaleString('en-GB')})
					))
				]
			}
		}

		throwToast("Artist T goods exceed $15!")	
		return true

	} else if (totalCost >= 30) {
		// Insert all 3 giveaway items
		throwToast("Artist T goods exceed $30!")
		form.submission = {
			data: {
				merchandisesToTransact: [
					...form.submission.data.merchandisesToTransact,
					...await Promise.all(['T15', 'T18', 'T20'].map(
						async m => ({
							... await getSingleArtistMerch('T', m), 
							artistId: {label: "T - Shan", value: "T"}, 
							qty: 1, 
							price: {label: "Giveaway", value: 0}, 
							datetime: new Date().toLocaleString('en-GB')})
					))
				]
			}
		}
		return true
	}
	return false
}

const updateModels = async (artistId=None) => {
	return await axios
		.get(`http://${SERVER_URL}/user/update/${artistId ?? ""}`)
		.then(res => res.data)
		.catch(async err => {
			var title = "Error occured!"
			var text = err.message
			console.log("EEEE", err)

			if (err.response?.data?.data?.error?.code ?? null == 429) {
				title = "Error due to Sheet API limit!"
				text = "Try again later..."
			}

			await Swal.fire({
				title: title,
				text: text,
				icon: 'error',
				timer: 1000,
				timerProgressBar: true
			}).then(() =>
				window.location.reload()
			)
		})
}

const getAllArtistIds = async () => {
	return await axios.get(`http://${SERVER_URL}/user/artistIds`).then(res => res.data)
}

const getAllArtists = async () => {
	return await axios.get(`http://${SERVER_URL}/user`).then(res => res.data)
}

const getArtist = async (artistId) => {
	return await axios.get(`http://${SERVER_URL}/user/${artistId}`).then(res => res.data)
}

const getArtistMerch = async (artistId) => {
	return await axios.get(`http://${SERVER_URL}/user/${artistId}/merch`).then(res => res.data)
}

const getSingleArtistMerch = async (artistId, merchId) => {
	var merch = await axios.get(`http://${SERVER_URL}/user/${artistId}/merch/${merchId}`).then(res => res.data.data)
	merch = {...merch, 
		initialPrice: {label: merch.initialPrice, value: currencyToFloat(merch.initialPrice)},
		merchId: {
			...merch.merchId,
			embedCode: merch.embedCode,
			imageLink: merch.imageLink,
		}
	}
	return merch
}

const updateMerch = async (transactions) => {
	return await axios.post(`http://${SERVER_URL}/user/merch`, transactions).then(res => res.data)
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
				// If applied, do not apply again
				if (!formTransaction.submission.data.isHandledADiscount) {
					if (handleADiscountTransaction(formTransaction)) {
						formTransaction.submission.data.isHandledADiscount = true
					}
				} else {
					formTransaction.submission.data.isHandledADiscount = false
				}

				if (!formTransaction.submission.data.isHandledTDiscount) {
					if (handleTDiscountTransaction(formTransaction)) {
						formTransaction.submission.data.isHandledTDiscount = true
					}
				} else {
					formTransaction.submission.data.isHandledTDiscount = false
				}
				break;

			default:
				break;
		}

		console.log(formTransaction)
		console.log(formTransaction.getComponent('artistId'))

		console.log(formTransaction.submission)

	})


	formTransaction.on('error', async errors => {
		console.log("ERR: ", errors)
		Swal.fire({
			title: 'Error!',
			text: JSON.stringify(errors),
			icon: 'error',
		})
	})

	formTransaction.on('componentError', async errors => {
		console.log("ERR: ", errors)
		Swal.fire({
			title: 'Error!',
			text: "Fill the form in order!",
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
