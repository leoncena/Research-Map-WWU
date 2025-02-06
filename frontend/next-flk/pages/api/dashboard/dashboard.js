import clientPromise from '../../../lib/mongodb'

export default async (req, res) => {
  try {
    // await clientPromise
    // `await clientPromise` will use the default database passed in the MONGODB_URI
    // However you can use another database (e.g. myDatabase) by replacing the `await clientPromise` with the following code:
    //
    const client = await clientPromise
    const db = client.db('FLK_Web')

    const amount_publications = await db.collection('publications').count({})

    const amount_authors = await db.collection('persons').count({})

    const amount_chairs = await db
      .collection('organisations')
      .find({ status: 5 })
      .count({})

    const amount_all = [amount_publications, amount_authors, amount_chairs]

    res.json(amount_all)
  } catch (e) {
    console.error(e)
  }
}
