

```dataviewjs
function convertToSlug(str) {
    return str.toLowerCase().replace(/ /g,'-')
		  .replace(/[-]+/g, '-').replace(/[^\w\u00C0-\u017F-]+/g,'');
}

const excludes = ["file", "aliases", "tags", "position", "links", "inlinks", "outlinks", "etags", "frontmatter", "lists", "tasks"];
let myFields = new Map();
dv.pages('"/"').forEach((page) => 
	Object.keys(page)
		.map(k => convertToSlug(k))
		.filter(k => !excludes.contains(k))
		.forEach(k => 
			myFields.set(k, (myFields.has(k) ? 1 + myFields.get(k) : 1))
		)
);
let myFieldsDV = dv.array(Array.from(myFields))
	.sort(([sluggedField, howManyNotes]) => howManyNotes, "desc");
let myDVHeaders = ["Slugged Field", "Count"];
dv.table(myDVHeaders, myFieldsDV);

dv.header(3, "Rare Fields:");
dv.table(myDVHeaders.concat(["Notes"]), 
		 myFieldsDV
		 .filter(([ignore, howManyNotes]) => howManyNotes < 3)
		 .map(([sluggedField, howManyNotes]) => 
			 [
			 sluggedField, 
			 howManyNotes, 
			 dv.pages('"/"').filter(page => 
				 Object.hasOwn(page, sluggedField)).file.link
			 ])
		 .sort(([sluggedField, hm, notes]) => sluggedField)
		);	
```