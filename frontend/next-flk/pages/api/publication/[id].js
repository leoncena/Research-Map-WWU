import clientPromise from '../../../lib/mongodb'

export default async (req, res) => {
  const { id } = req.query

  try {
    const client = await clientPromise
    const db = client.db('FLK_Web')

    const filter = { id: id }

    const publications = await db
      .collection('publications')
      .find(filter)
      .toArray()

    res.json(publications)
  } catch (e) {
    console.error(e)
  }
}
