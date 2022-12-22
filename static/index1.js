
window.onload = async () => {
	const formJson = await fetch('static/formio.json').then(res => res.text())
	console.log(formJson)
	await Formio.createForm(document.getElementById('formio'), JSON.parse(formJson));
}
