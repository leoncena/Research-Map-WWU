import clientPromise from '../../../lib/mongodb'

export default async (req, res) => {
  const { authorid } = req.query

  try {
    const client = await clientPromise
    const db = client.db('FLK_Web')

    const filter = { id: authorid }

    const latestPublications = await db
      .collection('persons')
      .find(filter)
      .project({ _id: 0 })
      .toArray()

    res.json(latestPublications[0])
  } catch (e) {
    console.error(e)
  }
}
