# Packete löschen

## ID der latest-Version ermitteln

``` bash
gh api \
  -H "Accept: application/vnd.github+json" \
  /users/$PKG_OWNER/packages/container/$PKG_NAME/versions \
  --paginate \
  | jq ".[] | select(.id != ${LATEST_ID}) | .id" \
  | while read ID; do
      echo "Deleting version $ID"
      gh api \
        --method DELETE \
        -H "Accept: application/vnd.github+json" \
        /users/$PKG_OWNER/packages/container/$PKG_NAME/versions/$ID
    done
```

Anschliessend

``` bash
gh api \
  -H "Accept: application/vnd.github+json" \
  /users/$PKG_OWNER/packages/container/$PKG_NAME/versions \
  --paginate \
  | jq ".[] | select(.id != ${LATEST_ID}) | .id" \
  | while read ID; do
      echo "Deleting version $ID"
      gh api \
        --method DELETE \
        -H "Accept: application/vnd.github+json" \
        /users/$PKG_OWNER/packages/container/$PKG_NAME/versions/$ID
    done
```
